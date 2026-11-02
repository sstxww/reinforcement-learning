"""Session s-20261102-509af6d2: isolated opening-upgrade timing ablation.

All games use the real pinned TavernGym Game, never a surrogate engine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .canary import run as run_original_baseline
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION_ID = "s-20261102-509af6d2"
POLICY_VERSION = "delay-opening-upgrade-v1"


class DelayedOpeningUpgradePolicy:
    """Ablate *only* the opening upgrade: defer turn 2 until turn 3.

    All other decisions fall back to the pinned deterministic baseline.
    Never mask away the sole legal action. Mandatory choices and playing
    cards still precede an upgrade; an action budget still ends the turn.
    """

    def __init__(self) -> None:
        self.baseline = BaselinePolicy()

    def act(self, observation: dict, context: dict | None = None) -> int:
        context = context or {}
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise ValueError("Expected nonempty 245-action mask")
        turn = int(context.get("turn", 0))
        used = int(context.get("actions_used", 0))
        if turn == 2 and mask[3] and int(mask.sum()) > 1:
            delayed = mask.copy()
            delayed[3] = False
            choice = self.baseline.act({**observation, "action_mask": delayed}, context)
        elif (turn == 3 and used < 85 and mask[3]
              and not mask[30:46].any()
              and not mask[46:196].any()):
            choice = 3
        else:
            choice = self.baseline.act(observation, context)
        if not mask[choice]:
            raise ValueError(f"Candidate selected illegal action {choice}")
        return int(choice)


def run_candidate(seed: int) -> dict:
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    policy = DelayedOpeningUpgradePolicy()
    decisions = 0
    upgrades = 0
    actions_this_turn = 0
    last_turn = -1

    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, actions_this_turn = turn, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat:
                game.bot_play(seat)
                continue
            f = np.frombuffer(game.observe2(0)[0], dtype="<f4").copy()
            c = np.frombuffer(game.observe2(0)[1], dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Unexpected observe2 dimensions")
            action = policy.act(
                {"features": f, "cards": c, "action_mask": mask},
                {"turn": turn, "actions_used": actions_this_turn},
            )
            if not mask[action]:
                raise ValueError("Illegal candidate action")
            game.step(0, action)
            decisions += 1
            actions_this_turn += 1
            upgrades += int(action == 3)
        if not progressed and not game.is_over():
            raise RuntimeError("TavernGym game stalled")

    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")
    placements = [int(x) for x in game.placements()]
    if sorted(placements) != list(range(1, 9)):
        raise ValueError("Invalid final eight-seat ranks")
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION_ID,
        "policy": POLICY_VERSION,
        "policy_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "model_sha256": None,
        "seed": seed,
        "completed": bool(game.is_over()),
        "turns": int(game.turn),
        "decisions": decisions,
        "upgrade_actions": upgrades,
        "placements": placements,
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.environ.get("GITHUB_SHA", ""),
    }
    validate(receipt)
    return receipt


def summarize(receipts: list[dict]) -> dict:
    places = [receipt["placements"][0] for receipt in receipts]
    return {
        "games": len(places),
        "seeds": [receipt["seed"] for receipt in receipts],
        "placements": places,
        "mean_rank": statistics.mean(places),
        "first_place_rate": sum(x == 1 for x in places) / len(places),
        "top_four_rate": sum(x <= 4 for x in places) / len(places),
    }


def experiment(seeds: list[int], out_dir: Path, report_path: Path) -> dict:
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("Provide nonempty, distinct independent seeds")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    controls, candidates = [], []
    for seed in seeds:
        original = run_original_baseline(seed, SESSION_ID, policy="baseline")
        control_path = out_dir / f"baseline-{seed}.json"
        control_path.write_text(json.dumps(original, indent=2), encoding="utf-8")
        controls.append(original)

        candidate = run_candidate(seed)
        candidate_path = out_dir / f"001-{seed}.json"
        candidate_path.write_text(json.dumps(candidate, indent=2), encoding="utf-8")
        candidates.append(candidate)
        print(f"seed={seed} control={original['placements'][0]} "
              f"candidate={candidate['placements'][0]} "
              f"candidate_decisions={candidate['decisions']}", flush=True)

    control_summary, candidate_summary = summarize(controls), summarize(candidates)
    report = {
        "session_id": SESSION_ID,
        "hypothesis": "Delay opening Tavern upgrade from turn 2 to turn 3",
        "engine": verify_engine(),
        "baseline": control_summary,
        "candidate": candidate_summary,
        "candidate_minus_baseline_mean_rank":
            candidate_summary["mean_rank"] - control_summary["mean_rank"],
        "paired_rank_differences": [
            b["placements"][0] - a["placements"][0]
            for a, b in zip(controls, candidates)
        ],
        "training_steps": 0,
        "method": "real eight-seat TavernGym Game, seat 0 vs seven official bots",
        "interpretation": "Descriptive small-sample ablation; no confirmed improvement",
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, default=[38101, 38102, 38103, 38104])
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(experiment(args.seeds, args.out_dir, args.report), indent=2))


if __name__ == "__main__":
    main()
