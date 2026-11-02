"""Measure TavernGym seat sensitivity with a baseline-controlled seat.

This is an evaluation instrument, not a policy improvement or self-play.
Each seat assignment runs a fresh real Game with seven official rule bots.
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


def validate_grid(seeds: list[int], seats: list[int]) -> None:
    if not seeds or not seats or len(seeds) * len(seats) > 12:
        raise ValueError("Require 1..12 finite seed/seat combinations")
    if len(set(seeds)) != len(seeds) or len(set(seats)) != len(seats):
        raise ValueError("Seeds and seats must be unique")
    if any(type(s) is not int or s < 0 or s > 7 for s in seats):
        raise ValueError("Seats must be integers from 0 through 7")
    if any(type(s) is not int or s < 0 for s in seeds):
        raise ValueError("Seeds must be nonnegative integers")


def play(seed: int, agent_id: str, seat: int) -> dict:
    validate_grid([seed], [seat])
    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid agent id")
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    if game.num_players != 8:
        raise RuntimeError("Expected an eight-player TavernGym game")
    policy = BaselinePolicy()
    decisions = 0
    actions_this_turn = 0
    last_turn = -1
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, actions_this_turn = turn, 0
        progress = False
        for current in range(game.num_players):
            if not game.needs_action(current):
                continue
            progress = True
            if current != seat:
                game.bot_play(current)
                continue
            fb, cb = game.observe2(seat)
            features = np.frombuffer(fb, dtype="<f4").copy()
            cards = np.frombuffer(cb, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(seat), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Unexpected observe2 contract")
            if not np.isfinite(features).all():
                raise ValueError("Nonfinite numeric observation")
            action = policy.act(
                {"features": features, "cards": cards, "action_mask": mask},
                {"turn": turn, "actions_used": actions_this_turn},
            )
            if action < 0 or action >= ACTIONS or not mask[action]:
                raise ValueError("Illegal baseline action")
            game.step(seat, action)
            decisions += 1
            actions_this_turn += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")
    placements = [int(x) for x in game.placements()]
    run_id = os.environ.get("GITHUB_RUN_ID")
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": "baseline",
        "evaluation_method": "seat-rotation-v1",
        "seat": seat,
        "agent_placement": placements[seat],
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": placements,
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "policy_sha256": hashlib.sha256(Path(__file__).with_name("baseline.py").read_bytes()).hexdigest(),
        "model_sha256": None,
        "workflow_run_url": (
            f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{run_id}"
            if run_id and os.environ.get("GITHUB_REPOSITORY") else None
        ),
    }
    validate(receipt)
    return receipt


def summarize(records: list[dict]) -> dict:
    if not records:
        raise ValueError("Cannot summarize zero games")
    summary = {}
    for seat in sorted({int(row["seat"]) for row in records}):
        subset = [r for r in records if r["seat"] == seat]
        ranks = [r["placements"][seat] for r in subset]
        summary[str(seat)] = {
            "games": len(subset),
            "seeds": [r["seed"] for r in subset],
            "placements": ranks,
            "mean_placement": statistics.mean(ranks),
            "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
            "first_place_rate": sum(x == 1 for x in ranks) / len(ranks),
        }
    return {
        "policy": "baseline",
        "games": len(records),
        "by_seat": summary,
        "interpretation": (
            "Descriptive only: seat assignments may change heroes/shop RNG and bot outcomes; "
            "small samples cannot establish seat advantage or policy improvement."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--seeds", type=int, nargs="+", required=True)
    parser.add_argument("--seats", type=int, nargs="+", required=True)
    parser.add_argument("--receipt-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    validate_grid(args.seeds, args.seats)
    records = []
    args.receipt_dir.mkdir(parents=True, exist_ok=True)
    for seed in args.seeds:
        for seat in args.seats:
            row = play(seed, args.agent_id, seat)
            filename = f"001-{seed}.json" if seat == 0 else f"rotated-{seed}-seat{seat}.json"
            target = args.receipt_dir / filename
            target.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({"receipt": str(target), "seat": seat, "placement": row["agent_placement"], "completed": row["completed"]}), flush=True)
            records.append(row)
    report = summarize(records)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
