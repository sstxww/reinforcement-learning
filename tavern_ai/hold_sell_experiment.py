"""Session-local ablation: do not automatically sell board minions.

This module deliberately leaves the shared baseline, canary and trainer unchanged.
All matches run on the pinned real TavernGym engine.
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
from .canary import run as run_baseline
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

POLICY_NAME = "hold_sell_v1"
DEFAULT_SEED = 34200
PAIR_SEEDS = (34201, 34202, 34203)


class HoldSellPolicy:
    """Play hand, level on baseline schedule, buy, then end; never auto-sell.

    Deliberately preserve the original baseline's discover priority and tier
    schedule. Change only the unconditional sell-before-buy behavior.
    """

    def act(self, observation: dict, context: dict | None = None) -> int:
        context = context or {}
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise ValueError("Expected nonempty 245-action mask")
        turn = int(context.get("turn", 0))
        used = int(context.get("actions_used", 0))

        def first(lo: int, hi: int) -> int | None:
            xs = np.flatnonzero(mask[lo:hi])
            return int(lo + xs[0]) if len(xs) else None

        mandatory = first(30, 46)
        if mandatory is not None:
            return mandatory
        if used >= 60 and mask[0]:
            return 0
        play = first(46, 126)
        if play is not None:
            return play
        if turn in {2, 5, 7, 9, 11} and mask[3]:
            return 3
        buy = first(8, 16)
        if buy is not None:
            return buy
        # Prefer stopping to selling units just because sell is legal.
        if mask[0]:
            return 0
        return int(np.flatnonzero(mask)[0])


def run_candidate(seed: int, agent_id: str) -> dict:
    import taverngym

    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid agent ID")
    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    policy = HoldSellPolicy()
    decisions = 0
    turn_actions = 0
    last_turn = -1
    illegal_actions = 0

    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, turn_actions = turn, 0
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            raw_features, raw_cards = game.observe2(0)
            features = np.frombuffer(raw_features, dtype="<f4").copy()
            cards = np.frombuffer(raw_cards, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if (features.shape, cards.shape, mask.shape) != ((FEATURES,), (CARDS,), (ACTIONS,)):
                raise ValueError("Unexpected pinned observe2 contract")
            action = policy.act(
                {"features": features, "cards": cards, "action_mask": mask},
                {"turn": turn, "actions_used": turn_actions},
            )
            if not mask[action]:
                illegal_actions += 1
                raise ValueError(f"Illegal hold-sell action: {action}")
            game.step(0, action)
            turn_actions += 1
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Candidate full-game safety limit exceeded")
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": POLICY_NAME,
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "illegal_actions": illegal_actions,
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "policy_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "model_sha256": None,
    }
    validate(receipt)
    if illegal_actions:
        raise ValueError("Illegal action counter was nonzero")
    return receipt


def summarize(records: list[dict]) -> dict:
    ranks = [r["placements"][0] for r in records]
    return {
        "games": len(records),
        "mean_placement": statistics.mean(ranks),
        "first_place_rate": sum(r == 1 for r in ranks) / len(ranks),
        "top4_rate": sum(r <= 4 for r in ranks) / len(ranks),
        "placements": ranks,
        "seeds": [r["seed"] for r in records],
    }


def save_receipt(path: Path, receipt: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--pair-seeds", type=int, nargs="+", default=list(PAIR_SEEDS))
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if len(args.pair_seeds) < 2 or len(set(args.pair_seeds + [args.seed])) != len(args.pair_seeds) + 1:
        raise ValueError("Need at least two distinct held-out seeds and independent canary seed")

    own = run_candidate(args.seed, args.agent_id)
    save_receipt(args.out_dir / f"001-{args.seed}.json", own)
    control, candidate = [], []
    for seed in args.pair_seeds:
        base = run_baseline(seed, args.agent_id, policy="baseline")
        trial = run_candidate(seed, args.agent_id)
        control.append(base)
        candidate.append(trial)
        save_receipt(args.out_dir / f"control-{seed}.json", base)
        save_receipt(args.out_dir / f"candidate-{seed}.json", trial)

    base_summary = summarize(control)
    candidate_summary = summarize(candidate)
    report = {
        "experiment": "hold_sell_v1_paired",
        "hypothesis": "Skipping optional auto-sells might improve rank against seven official bots",
        "environment": verify_engine(),
        "policy_sha256": own["policy_sha256"],
        "base_git_sha": os.getenv("GITHUB_SHA", ""),
        "training_timesteps": 0,
        "own_full_game": {
            "seed": args.seed,
            "completed": own["completed"],
            "rank": own["placements"][0],
            "decisions": own["decisions"],
        },
        "control": base_summary,
        "candidate": candidate_summary,
        "paired_rank_deltas_candidate_minus_control": [
            new["placements"][0] - old["placements"][0]
            for old, new in zip(control, candidate)
        ],
        "interpretation": "Small descriptive sample; no statistical or Arena Elo claim",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
