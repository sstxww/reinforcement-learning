"""Isolated 30..45 choice-band position-bias ablation on the real TavernGym engine.

This deliberately does not claim card-quality ranking: the sole hypothesis is
that always selecting the first available choice introduces positional bias.
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
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

CHOICE_START, CHOICE_END = 30, 46


class LastChoicePolicy(BaselinePolicy):
    """Choose highest-index legal 30..45 option, otherwise unchanged V0."""

    def act(self, observation: dict, context: dict | None = None) -> int:
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise ValueError("Expected 245-action nonempty mask")
        options = np.flatnonzero(mask[CHOICE_START:CHOICE_END])
        if len(options):
            return CHOICE_START + int(options[-1])
        return super().act(observation, context)


def play(seed: int, agent_id: str, policy: str) -> dict:
    import taverngym

    if policy not in ("baseline", "last-choice"):
        raise ValueError("Unknown candidate policy")
    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid session agent ID")
    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    baseline, candidate = BaselinePolicy(), LastChoicePolicy()
    decisions = 0
    opportunities = 0
    interventions = 0
    illegal_actions = 0
    actions_this_turn = 0
    last_turn = -1
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, actions_this_turn = turn, 0
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(0)
            f = np.frombuffer(fbytes, dtype="<f4").copy()
            c = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("TavernGym observe2 contract mismatch")
            if not mask.any() or not np.isfinite(f).all():
                raise ValueError("Invalid candidate observation")
            obs = {"features": f, "cards": c, "action_mask": mask}
            context = {"turn": turn, "actions_used": actions_this_turn}
            baseline_action = baseline.act(obs, context)
            action = (candidate if policy == "last-choice" else baseline).act(obs, context)
            options = np.flatnonzero(mask[CHOICE_START:CHOICE_END])
            if len(options) >= 2:
                opportunities += 1
                if action != baseline_action:
                    interventions += 1
            if not 0 <= int(action) < ACTIONS or not mask[int(action)]:
                illegal_actions += 1
                raise ValueError(f"Illegal candidate action {action}")
            game.step(0, int(action))
            actions_this_turn += 1
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("Real TavernGym match stalled")
    if not game.is_over():
        raise RuntimeError("Real TavernGym match exceeded 30000 scheduler steps")
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": policy,
        "seed": seed,
        "completed": bool(game.is_over()),
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": None,
        "policy_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "choice_opportunities": opportunities,
        "candidate_choice_interventions": interventions,
        "illegal_actions": illegal_actions,
    }
    validate(result)
    return result


def summarize(records: list[dict]) -> dict:
    ranks = [r["placements"][0] for r in records]
    return {
        "games": len(records),
        "seeds": [r["seed"] for r in records],
        "rankings": ranks,
        "mean_placement": statistics.mean(ranks),
        "first_place_rate": sum(x == 1 for x in ranks) / len(ranks),
        "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
        "choice_opportunities": sum(r["choice_opportunities"] for r in records),
        "candidate_choice_interventions": sum(r["candidate_choice_interventions"] for r in records),
    }


def experiment(session: str, seed: int, pairs: int, root: Path) -> dict:
    if not session.startswith("s-") or "/" in session or "\\" in session:
        raise ValueError("Invalid session ID")
    if not 1 <= pairs <= 10:
        raise ValueError("pairs must be 1..10")
    receipts_dir = root / "experiments" / session
    reports_dir = root / "reports" / session
    receipts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    canary = play(seed, session, "last-choice")
    (receipts_dir / f"001-{seed}.json").write_text(
        json.dumps(canary, indent=2), encoding="utf-8"
    )
    baseline_records, candidate_records = [], []
    for i in range(pairs):
        current_seed = seed + i + 1
        control = play(current_seed, session, "baseline")
        treatment = play(current_seed, session, "last-choice")
        baseline_records.append(control)
        candidate_records.append(treatment)
        for policy, record in (("baseline", control), ("last-choice", treatment)):
            (receipts_dir / f"paired-{policy}-{current_seed}.json").write_text(
                json.dumps(record, indent=2), encoding="utf-8"
            )
    before = summarize(baseline_records)
    after = summarize(candidate_records)
    report = {
        "session": session,
        "hypothesis": "Choose last rather than first legal 30..45 choice action",
        "seed_canary": seed,
        "candidate_canary_rank": canary["placements"][0],
        "candidate_canary_decisions": canary["decisions"],
        "candidate_canary_completed": canary["completed"],
        "candidate_canary_interventions": canary["candidate_choice_interventions"],
        "baseline": before,
        "candidate": after,
        "paired_rank_delta": [
            a - b for a, b in zip(after["rankings"], before["rankings"])
        ],
        "paired_mean_placement_delta": after["mean_placement"] - before["mean_placement"],
        "engine": "TavernGym 1.1.0",
        "engine_source_hash": canary["engine_source_hash"],
        "policy_source_sha256": canary["policy_source_sha256"],
        "ppo_training_steps": 0,
        "best_promoted": False,
        "uncertainty": "Descriptive paired sample only. Zero interventions means no causal exposure.",
    }
    (reports_dir / "discover-last-paired.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False))
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--session", required=True)
    p.add_argument("--seed", type=int, default=49001)
    p.add_argument("--pairs", type=int, default=3)
    p.add_argument("--root", type=Path, default=Path("."))
    a = p.parse_args()
    experiment(a.session, a.seed, a.pairs, a.root)


if __name__ == "__main__":
    main()
