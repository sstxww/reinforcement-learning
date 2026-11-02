"""Isolated real TavernGym full-game seeded-trajectory reproducibility audit.

Checks the action-observation transcript as well as the final placement. This is
an engineering audit of the existing V0 baseline, not an improved game policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

TRACE_FIELDS = ("seed", "placements", "turns", "decisions",
                "truncated_combats", "turn_limit_end", "trace_sha256",
                "engine_source_hash", "engine_version")


def order_for_seeds(seeds: list[int]) -> list[int]:
    if len(seeds) < 2 or len(seeds) > 10 or len(set(seeds)) != len(seeds):
        raise ValueError("Require 2..10 distinct seeds")
    return seeds + list(reversed(seeds))


def compare_replays(first: dict, second: dict) -> dict:
    """Do not compare timestamps, GitHub run metadata or agent_id."""
    differing = [key for key in TRACE_FIELDS if first.get(key) != second.get(key)]
    return {
        "seed": first["seed"],
        "identical": not differing,
        "different_fields": differing,
        "first_trace_sha256": first.get("trace_sha256"),
        "replayed_trace_sha256": second.get("trace_sha256"),
        "first_placement": first["placements"][0],
        "replayed_placement": second["placements"][0],
    }


def play(seed: int, agent_id: str) -> dict:
    """Run actual eight-player TavernGym until Game.is_over() with a trace hash."""
    import taverngym

    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid agent ID")
    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    baseline = BaselinePolicy()
    digest = hashlib.sha256()
    decisions = 0
    last_turn = -1
    actions_this_turn = 0

    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn = turn
            actions_this_turn = 0
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue

            features_bytes, cards_bytes = game.observe2(0)
            mask_bytes = game.legal_mask(0)
            features = np.frombuffer(features_bytes, dtype="<f4").copy()
            cards = np.frombuffer(cards_bytes, dtype="<i4").copy()
            mask = np.frombuffer(mask_bytes, dtype=np.uint8).astype(bool)
            if (features.shape != (FEATURES,) or cards.shape != (CARDS,)
                    or mask.shape != (ACTIONS,)):
                raise ValueError("Unexpected observe2 contract")
            if not np.isfinite(features).all():
                raise ValueError("Non-finite observe2 features")
            action = int(baseline.act(
                {"features": features, "cards": cards, "action_mask": mask},
                {"turn": turn, "actions_used": actions_this_turn},
            ))
            if action < 0 or action >= ACTIONS or not mask[action]:
                raise ValueError(f"Illegal policy action {action}")
            # The hash is sensitive to even a single different state or action.
            digest.update(struct.pack("<III", turn, decisions, action))
            digest.update(features_bytes)
            digest.update(cards_bytes)
            digest.update(mask_bytes)
            game.step(0, action)
            actions_this_turn += 1
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("TavernGym stalled")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")

    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": "baseline",
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": None,
        "trace_sha256": digest.hexdigest(),
        "trace_algorithm": "sha256(turn,decision,action,observe2_features,cards,legal_mask)",
    }
    validate(receipt)
    return receipt


def audit(seeds: list[int], agent_id: str) -> tuple[dict, dict]:
    ordered_seeds = order_for_seeds(seeds)
    games = [play(seed, agent_id) for seed in ordered_seeds]
    n = len(seeds)
    comparisons = [compare_replays(games[i], games[2 * n - 1 - i])
                   for i in range(n)]
    report = {
        "experiment": "seeded_full_game_replay_determinism",
        "session_id": agent_id,
        "game_engine": "TavernGym (real engine, observe2)",
        "candidate_policy": "unchanged V0 baseline",
        "note": "Reproducibility audit only; not a model-strength comparison",
        "seeds": seeds,
        "execution_order": ordered_seeds,
        "full_matches": len(games),
        "seed_pairs": n,
        "comparisons": comparisons,
        "all_reproducible": all(c["identical"] for c in comparisons),
        "all_games_completed": all(g["completed"] for g in games),
        "placements_first_pass": [g["placements"][0] for g in games[:n]],
        "first_pass_mean_placement": sum(g["placements"][0] for g in games[:n]) / n,
        "first_pass_top4_rate": sum(g["placements"][0] <= 4 for g in games[:n]) / n,
        "first_pass_first_place_rate": sum(g["placements"][0] == 1 for g in games[:n]) / n,
        "ppo_training_steps": 0,
        "checkpoint": None,
    }
    return report, games[0]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--agent-id", required=True)
    p.add_argument("--seeds", nargs="+", type=int, default=[36011, 36012, 36013])
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    report, receipt = audit(args.seeds, args.agent_id)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if not report["all_reproducible"]:
        raise SystemExit("Cross-order seeded replay mismatch; inspect saved report")


if __name__ == "__main__":
    main()
