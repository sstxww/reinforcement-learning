"""Trace real, masked model behavior without calling forced actions model decisions.

This experiment is guarded model inference, NOT a pure model-strength test.
It cannot prove a rank-eight cause without matched context and enough seeds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .checkpoint_registry import file_sha256, validate_registry
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION = "s-20261102-decfc670"
TURN_BUDGET = 40


def classify(action: int) -> str:
    if action == 0:
        return "end_turn"
    if action == 3:
        return "upgrade"
    if 8 <= action < 16:
        return "buy"
    if 16 <= action < 23:
        return "sell"
    if 46 <= action < 126:
        return "play"
    return "other"


def decide_with_guard(mask: np.ndarray, proposed: int | None, used: int) -> tuple[int, bool]:
    if used >= TURN_BUDGET:
        if not mask[0]:
            raise RuntimeError("Turn budget reached but END_TURN illegal")
        return 0, True
    if proposed is None or proposed < 0 or proposed >= len(mask) or not mask[proposed]:
        raise ValueError("Model predicted an illegal action")
    return proposed, False


def trace(seed: int, model, model_hash: str) -> dict:
    if type(seed) is not int or seed < 0:
        raise ValueError("Invalid trace seed")
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    if game.num_players != 8:
        raise RuntimeError("Expected eight seats")
    current_turn = -1
    used = 0
    decisions = 0
    forced = 0
    model_ends = 0
    missed_legal_buy_ends = 0
    legal_buy_decisions = 0
    legal_buy_turns = set()
    buy_count = 0
    same_action_state_count = 0
    last_action = None
    last_state = None
    hist = Counter()
    per_turn = {}
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != current_turn:
            current_turn, used, last_state, last_action = turn, 0, None, None
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            fb, cb = game.observe2(0)
            features = np.frombuffer(fb, dtype="<f4").copy()
            cards = np.frombuffer(cb, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Wrong pinned observe2 layout")
            state_hash = hashlib.blake2b(fb + cb, digest_size=12).hexdigest()
            if not np.isfinite(features).all():
                raise ValueError("Non-finite features")
            legal_buy = bool(mask[8:16].any())
            if legal_buy:
                legal_buy_decisions += 1
                legal_buy_turns.add(turn)
            if used >= TURN_BUDGET:
                action, guarded = decide_with_guard(mask, None, used)
            else:
                proposed, _ = model.predict(
                    {"features": features, "cards": cards}, action_masks=mask, deterministic=True
                )
                action, guarded = decide_with_guard(mask, int(np.asarray(proposed).item()), used)
            if last_state == state_hash and last_action == action and not guarded:
                same_action_state_count += 1
            last_state, last_action = state_hash, action
            family = classify(action)
            hist[family] += 1
            bucket = per_turn.setdefault(str(turn), {"model_ends": 0, "legal_buy_decisions": 0, "buys": 0, "forced": 0})
            bucket["legal_buy_decisions"] += int(legal_buy)
            if guarded:
                forced += 1
                bucket["forced"] += 1
            if not guarded and action == 0:
                model_ends += 1
                bucket["model_ends"] += 1
                if legal_buy:
                    missed_legal_buy_ends += 1
            if family == "buy":
                buy_count += 1
                bucket["buys"] += 1
            if not mask[action]:
                raise ValueError("Illegal model or forced action")
            game.step(0, action)
            used += 1
            decisions += 1
        if not progressed and not game.is_over():
            raise RuntimeError("Engine stalled")
    if not game.is_over():
        raise RuntimeError("Full-game loop cap exceeded")
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION,
        "policy": "guarded_model_diagnostic",
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "model_sha256": model_hash,
        "guard_forced_end_turns": forced,
        "model_chosen_end_turns": model_ends,
        "legal_buy_opportunity_decisions": legal_buy_decisions,
        "legal_buy_opportunity_turns": len(legal_buy_turns),
        "model_ends_with_legal_buy": missed_legal_buy_ends,
        "actual_buys": buy_count,
        "repeated_identical_state_and_action": same_action_state_count,
        "action_categories": dict(hist),
        "per_turn": per_turn,
        "method": "guarded observation-only masked diagnostic; not pure model performance",
    }
    validate(receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[86251, 86252])
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= len(args.seeds) <= 4 or len(set(args.seeds)) != len(args.seeds):
        raise ValueError("Require 1..4 unique seeds")
    registry = validate_registry(json.loads(args.registry.read_text(encoding="utf-8")))
    entry = next(e for e in registry["entries"] if e["model_id"] == "v2-learning-41413557445")
    actual_hash = file_sha256(args.model)
    if actual_hash != entry["model_sha256"]:
        raise ValueError("Wrong model checksum")
    from sb3_contrib import MaskablePPO

    model = MaskablePPO.load(str(args.model), device="cpu")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    receipts = []
    for seed in args.seeds:
        result = trace(seed, model, actual_hash)
        path = args.out_dir / f"002-{seed}.json"
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        receipts.append(result)
        print(json.dumps({"seed": seed, "placement": result["placements"][0],
                          "buys": result["actual_buys"],
                          "model_ends_with_legal_buy": result["model_ends_with_legal_buy"]}), flush=True)
    summary = {
        "session": SESSION,
        "kind": "guarded real eight-seat model-action diagnostic",
        "model_sha256": actual_hash,
        "seeds": args.seeds,
        "game_count": len(receipts),
        "placements": [r["placements"][0] for r in receipts],
        "total_buys": sum(r["actual_buys"] for r in receipts),
        "total_legal_buy_opportunity_decisions": sum(r["legal_buy_opportunity_decisions"] for r in receipts),
        "total_model_ends_with_legal_buy": sum(r["model_ends_with_legal_buy"] for r in receipts),
        "total_guard_forced_ends": sum(r["guard_forced_end_turns"] for r in receipts),
        "caution": "Guard-assisted play is not unguarded model strength. Legal mask does not alone establish economic optimality."
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
