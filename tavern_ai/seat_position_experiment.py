"""Isolated real-TavernGym audit: does the evaluated seat affect baseline results?

Each match controls exactly one seat and delegates all remaining seats to the
upstream official scripted bot. These are genuine Game-to-is_over() runs.
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


def verify_controlled_receipt(record: dict) -> bool:
    validate(record)
    seat = record.get("controlled_seat")
    places = record["placements"]
    if type(seat) is not int or not 0 <= seat < 8:
        raise ValueError("Controlled seat must be 0..7")
    if sorted(places) != list(range(1, 9)):
        raise ValueError("Placements are not a complete eight-player permutation")
    if record.get("controlled_rank") != places[seat]:
        raise ValueError("Controlled rank does not match controlled seat")
    if record.get("policy") != "baseline":
        raise ValueError("This experiment requires the original baseline policy")
    return True


def play(seed: int, agent_id: str, controlled_seat: int) -> dict:
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("Seed must be a uint32")
    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid agent ID")
    if type(controlled_seat) is not int or not 0 <= controlled_seat < 8:
        raise ValueError("Controlled seat must be 0..7")
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    if game.num_players != 8:
        raise RuntimeError("Expected real eight-seat TavernGym game")
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
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != controlled_seat:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(seat)
            features = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(seat), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("TavernGym observe2 contract mismatch")
            action = int(policy.act(
                {"features": features, "cards": cards, "action_mask": mask},
                {"turn": turn, "actions_used": actions_this_turn},
            ))
            if not 0 <= action < ACTIONS or not mask[action]:
                raise ValueError(f"Illegal action {action} for seat {seat}")
            game.step(seat, action)
            decisions += 1
            actions_this_turn += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled without a legal move")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")
    places = [int(v) for v in game.placements()]
    record = {
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
        "placements": places,
        "controlled_seat": controlled_seat,
        "controlled_rank": places[controlled_seat],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": None,
        "policy_sha256": hashlib.sha256(
            Path(__file__).with_name("baseline.py").read_bytes()
        ).hexdigest(),
    }
    verify_controlled_receipt(record)
    return record


def summarize(records: list[dict]) -> dict:
    if not records:
        raise ValueError("Need at least one completed match")
    for record in records:
        verify_controlled_receipt(record)
    ranks = [r["controlled_rank"] for r in records]
    return {
        "games": len(records),
        "ranks": ranks,
        "seeds": [r["seed"] for r in records],
        "mean_placement": statistics.mean(ranks),
        "top4_rate": sum(r <= 4 for r in ranks) / len(ranks),
        "first_place_rate": sum(r == 1 for r in ranks) / len(ranks),
    }


def run_experiment(agent_id: str, seed: int, pair_seeds: list[int],
                   out_dir: Path, report_path: Path) -> dict:
    if not pair_seeds or seed in pair_seeds or len(pair_seeds) != len(set(pair_seeds)):
        raise ValueError("Canary and paired seeds must all be distinct")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    canary = play(seed, agent_id, controlled_seat=4)
    (out_dir / f"001-{seed}.json").write_text(
        json.dumps(canary, indent=2), encoding="utf-8"
    )
    arms = {0: [], 4: []}
    for pair_seed in pair_seeds:
        for seat in (0, 4):
            record = play(pair_seed, agent_id, seat)
            arms[seat].append(record)
            (out_dir / f"pair-{pair_seed}-seat{seat}.json").write_text(
                json.dumps(record, indent=2), encoding="utf-8"
            )
    deltas = [a["controlled_rank"] - b["controlled_rank"]
              for a, b in zip(arms[4], arms[0])]
    report = {
        "hypothesis": "The fixed seat-zero evaluation convention may mask seat-dependent outcomes",
        "experiment": "Same untouched BaselinePolicy controls seat 0 or 4 against seven official TavernGym scripted bots",
        "canary": {"seed": seed, "controlled_seat": 4,
                   "controlled_rank": canary["controlled_rank"],
                   "decisions": canary["decisions"]},
        "seat_0": summarize(arms[0]),
        "seat_4": summarize(arms[4]),
        "paired_seat4_minus_seat0_ranks": deltas,
        "paired_mean_delta": statistics.mean(deltas),
        "environment": canary["engine_version"],
        "engine_source_hash": canary["engine_source_hash"],
        "policy_sha256": canary["policy_sha256"],
        "ppo_gradient_steps": 0,
        "model_checkpoint": None,
        "caveat": "Seat changes also alter assigned heroes/opponents and action order; this is an evaluation sensitivity audit, NOT an improved policy or causal seat advantage.",
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--agent-id", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--pair-seeds", type=int, nargs="+", required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(
        run_experiment(a.agent_id, a.seed, a.pair_seeds, a.out_dir, a.report),
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
