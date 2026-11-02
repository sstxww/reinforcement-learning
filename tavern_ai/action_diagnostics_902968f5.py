"""Public-observation-only trace for one authentic unmodified model-controlled game.

Diagnostic only. No safety override, no synthetic completed-game receipt,
and no inference from unobserved player state. A capped/stalled game is failure.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .release_integrity import sha256_file

ACTION_RANGES = (
    ("end_turn", 0, 1),
    ("refresh", 1, 2),
    ("freeze", 2, 3),
    ("upgrade", 3, 4),
    ("buy", 8, 16),
    ("sell", 16, 23),
    ("choose", 30, 46),
    ("play", 46, 126),
    ("magnetize", 126, 196),
)


def family(action: int) -> str:
    if not 0 <= int(action) < ACTIONS:
        raise ValueError("Action outside pinned contract")
    for name, lo, hi in ACTION_RANGES:
        if lo <= action < hi:
            return name
    return "other"


def summarize_actions(records: list[dict]) -> dict:
    counts = collections.Counter(x["family"] for x in records)
    legal_buy = sum(bool(x["legal_buy"]) for x in records)
    actual_buy = sum(x["family"] == "buy" for x in records)
    end_with_buy = sum(x["family"] == "end_turn" and x["legal_buy"] for x in records)
    return {
        "decisions": len(records),
        "action_families": dict(sorted(counts.items())),
        "legal_buy_opportunity_decisions": legal_buy,
        "actual_buy_actions": actual_buy,
        "buy_rate_given_legal_decision": actual_buy / legal_buy if legal_buy else None,
        "end_turn_when_buy_legal": end_with_buy,
        "end_turn_without_legal_buy": sum(
            x["family"] == "end_turn" and not x["legal_buy"] for x in records
        ),
        "max_same_action_streak": max((x["same_action_streak"] for x in records), default=0),
        "consecutive_identical_public_prestate": sum(
            bool(x["identical_prestate_as_previous"]) for x in records
        ),
        "max_turn_actions": max(collections.Counter(x["turn"] for x in records).values(), default=0),
        "end_turn_actions": sum(x["family"] == "end_turn" for x in records),
        "forced_end_turn_actions": 0,
    }


def run(seed: int, model_path: Path, expected_sha: str,
        output: Path, *, max_controlled_actions: int = 1500,
        max_actions_per_turn: int = 300, max_engine_cycles: int = 30000) -> dict:
    if not (1 <= max_controlled_actions <= 3000):
        raise ValueError("Bounded controlled action budget 1..3000 required")
    if not (1 <= max_actions_per_turn <= 500):
        raise ValueError("Bounded per-turn action budget 1..500 required")
    if sha256_file(model_path) != expected_sha:
        raise ValueError("Model checkpoint identity mismatch")
    engine = verify_engine()
    import taverngym
    from sb3_contrib import MaskablePPO

    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    records: list[dict] = []
    last_turn = None
    turn_actions = 0
    last_action = None
    last_hash = None
    same_streak = 0
    stop_reason = None
    for _ in range(max_engine_cycles):
        if game.is_over():
            break
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            turn = int(game.turn)
            if turn != last_turn:
                last_turn, turn_actions = turn, 0
            if len(records) >= max_controlled_actions:
                stop_reason = "controlled_action_budget_exceeded"
                break
            if turn_actions >= max_actions_per_turn:
                stop_reason = "per_turn_action_budget_exceeded"
                break
            fbytes, cbytes = game.observe2(0)
            features = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            mask_bytes = game.legal_mask(0)
            mask = np.frombuffer(mask_bytes, dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise RuntimeError("Native public observe2 contract mismatch")
            if not mask.any():
                raise RuntimeError("No legal actions")
            state_hash = hashlib.sha256(fbytes + cbytes + mask_bytes).hexdigest()[:16]
            proposed, _ = model.predict(
                {"features": features, "cards": cards},
                action_masks=mask, deterministic=True,
            )
            action = int(proposed)
            if not mask[action]:
                raise RuntimeError("Illegal unmodified model action")
            same_streak = same_streak + 1 if last_action == action else 1
            records.append({
                "turn": turn, "action": action, "family": family(action),
                "legal_buy": bool(mask[8:16].any()),
                "legal_buy_slots": int(mask[8:16].sum()),
                "legal_play": bool(mask[46:126].any()),
                "legal_upgrade": bool(mask[3]),
                "board_count_public_feature_33": float(features[33]),
                "hand_count_public_feature_34": float(features[34]),
                "state_hash": state_hash,
                "identical_prestate_as_previous": state_hash == last_hash,
                "same_action_streak": same_streak,
            })
            last_hash, last_action = state_hash, action
            game.step(0, action)
            turn_actions += 1
        if stop_reason is not None:
            break
        if not progressed:
            stop_reason = "simulator_stalled"
            break
    if not game.is_over() and stop_reason is None:
        stop_reason = "engine_cycle_budget_exceeded"
    completed = bool(game.is_over())
    stats = summarize_actions(records)
    by_turn = {}
    for row in records:
        key = str(row["turn"])
        s = by_turn.setdefault(key, {"decisions": 0, "legal_buy_decisions": 0,
                                      "buys": 0, "ends": 0, "end_with_legal_buy": 0,
                                      "max_board_count_observed": None})
        s["decisions"] += 1
        s["legal_buy_decisions"] += int(row["legal_buy"])
        s["buys"] += int(row["family"] == "buy")
        s["ends"] += int(row["family"] == "end_turn")
        s["end_with_legal_buy"] += int(row["family"] == "end_turn" and row["legal_buy"])
        val = row["board_count_public_feature_33"]
        s["max_board_count_observed"] = (
            val if s["max_board_count_observed"] is None else max(val, s["max_board_count_observed"])
        )
    result = {
        "schema": 1,
        "kind": "unmodified_model_public_action_trace",
        "engine": engine, "seed": seed, "model_sha256": expected_sha,
        "source_git_sha": os.getenv("GITHUB_SHA", ""),
        "completed": completed, "stop_reason": None if completed else stop_reason,
        "controlled_actions": stats, "turn_summary": by_turn,
        "placements": [int(x) for x in game.placements()] if completed else None,
        "last_60_public_decisions": records[-60:],
        "first_30_public_decisions": records[:30],
        "unique_state_hashes": len(set(x["state_hash"] for x in records)),
        "note": "Failure trace is not a completed match receipt; no fallback policy, no forced ends.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=927104)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-actions", type=int, default=1500)
    parser.add_argument("--max-actions-per-turn", type=int, default=300)
    args = parser.parse_args()
    result = run(args.seed, args.model, args.expected_sha, args.output,
                 max_controlled_actions=args.max_actions,
                 max_actions_per_turn=args.max_actions_per_turn)
    print(json.dumps({k: result[k] for k in
                     ("seed", "completed", "stop_reason", "controlled_actions", "placements")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
