"""Isolated TavernGym 1.1.0 early-upgrade policy ablation (real eight-seat games).

No changes to the shared baseline or simulator. Both arms use the same
55-action turn budget for safety; only upgrade priority differs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION_ID = "s-20261102-9a484c57"
UPGRADE_TURNS = frozenset({2, 5, 7, 9, 11})
ACTION_BUDGET = 55


def select_action(observation: dict, context: dict, early_upgrade: bool) -> int:
    """Prioritize one legal upgrade on scheduled turns, preserving mandatory picks."""
    mask = np.asarray(observation["action_mask"], dtype=bool)
    if mask.shape != (ACTIONS,) or not mask.any():
        raise ValueError("Expected 245 nonempty action mask")
    used = int(context.get("actions_used", 0))
    if used >= ACTION_BUDGET and mask[0]:
        return 0
    mandatory = np.flatnonzero(mask[30:46])
    if len(mandatory):
        return 30 + int(mandatory[0])
    if (
        early_upgrade
        and int(context.get("turn", -1)) in UPGRADE_TURNS
        and not bool(context.get("upgraded_this_turn", False))
        and mask[3]
    ):
        return 3
    return BaselinePolicy().act(observation, context)


def play(seed: int, mode: str, agent_id: str = SESSION_ID) -> dict:
    """Actually play to Game.is_over() against seven TavernGym scripted seats."""
    if mode not in {"baseline", "early-upgrade"}:
        raise ValueError("Unsupported policy arm")
    import taverngym
    engine = verify_engine()
    game = taverngym.Game(seed=int(seed))
    decisions = 0
    forced_end_turns = 0
    priority_upgrades = 0
    actions_this_turn = 0
    upgraded_this_turn = False
    last_turn = -1
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn = turn
            actions_this_turn = 0
            upgraded_this_turn = False
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            features_bytes, cards_bytes = game.observe2(0)
            features = np.frombuffer(features_bytes, dtype="<f4").copy()
            cards = np.frombuffer(cards_bytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Unexpected pinned observe2 contract")
            observation = {"features": features, "cards": cards, "action_mask": mask}
            context = {"turn": turn, "actions_used": actions_this_turn,
                       "upgraded_this_turn": upgraded_this_turn}
            action = select_action(observation, context, mode == "early-upgrade")
            if not mask[action]:
                raise ValueError(f"Illegal action {action} at turn {turn}")
            if action == 0 and actions_this_turn >= ACTION_BUDGET:
                forced_end_turns += 1
            if action == 3:
                if mode == "early-upgrade" and turn in UPGRADE_TURNS and not upgraded_this_turn:
                    priority_upgrades += 1
                upgraded_this_turn = True
            game.step(0, action)
            decisions += 1
            actions_this_turn += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")

    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": mode,
        "policy_version": "upgrade-priority-v1" if mode == "early-upgrade" else "bounded-v0",
        "seed": int(seed),
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "illegal_actions": 0,
        "forced_end_turns": forced_end_turns,
        "priority_upgrades": priority_upgrades,
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": None,
    }
    validate(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, nargs="+", default=[42021, 42022, 42023])
    parser.add_argument("--output-root", type=Path, default=Path("experiments") / SESSION_ID)
    parser.add_argument("--report", type=Path,
                        default=Path("reports") / SESSION_ID / "upgrade-paired.json")
    args = parser.parse_args()
    if len(args.seeds) != 3 or len(set(args.seeds)) != 3:
        parser.error("exactly three distinct seeds required")
    args.output_root.mkdir(parents=True, exist_ok=True)
    records = {}
    for mode in ("baseline", "early-upgrade"):
        rows = []
        for n, seed in enumerate(args.seeds):
            receipt = play(seed, mode)
            filename = f"001-{seed}.json" if mode == "early-upgrade" and n == 0 else f"{mode}-{seed}.json"
            path = args.output_root / filename
            path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            rows.append(receipt)
            print(json.dumps({"policy": mode, "seed": seed, "placement": receipt["placements"][0],
                              "decisions": receipt["decisions"], "completed": True}))
        records[mode] = rows

    def summary(rows):
        places = [r["placements"][0] for r in rows]
        return {"games": len(places), "placements": places, "mean_placement": sum(places) / len(places),
                "top4_rate": sum(p <= 4 for p in places) / len(places),
                "first_place_rate": sum(p == 1 for p in places) / len(places),
                "mean_decisions": sum(r["decisions"] for r in rows) / len(rows),
                "total_forced_ends": sum(r["forced_end_turns"] for r in rows),
                "total_priority_upgrades": sum(r["priority_upgrades"] for r in rows)}
    a, b = records["baseline"], records["early-upgrade"]
    report = {
        "session_id": SESSION_ID,
        "hypothesis": "Upgrading before playing held cards on scheduled turns can improve placement",
        "environment": "TavernGym 1.1.0",
        "engine_source_hash": b[0]["engine_source_hash"],
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "strategy_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "seeds": args.seeds,
        "action_budget_each_turn": ACTION_BUDGET,
        "ppo_training_steps": 0,
        "baseline": summary(a),
        "candidate": summary(b),
        "paired_placement_delta_candidate_minus_baseline": [
            x["placements"][0] - y["placements"][0] for x, y in zip(b, a)
        ],
        "inference": "Descriptive three-pair pilot only. Do not infer a strength gain.",
        "model_checkpoint": None,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(args.report), "baseline": report["baseline"],
                      "candidate": report["candidate"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
