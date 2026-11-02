"""Real TavernGym action-opportunity trace for released V2 PPO (research only).

Uses seat-0 observe2 and legal mask. No hidden state enters the policy. A
safety-guarded match is never counted as a raw, guard-free model performance win.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION = "s-20261102-94a71ba0"
RELEASE = "v2-learning-41413557445"
RELEASE_SHA256 = "73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a"


def action_kind(action: int) -> str:
    """Only label engine action bands validated against the pinned contract."""
    if action == 0:
        return "end_turn"
    if action == 3:
        return "upgrade"
    if 8 <= action < 16:
        return "buy"
    if 16 <= action < 23:
        return "sell"
    if 30 <= action < 46:
        return "mandatory_choice"
    if 46 <= action < 126:
        return "play"
    return "other"


def record_action(summary: dict, turns: dict, turn: int, mask: np.ndarray,
                  proposed: int, executed: int, forced: bool, streak: int) -> int:
    """Track offered legal BUY vs chosen BUY, never equate zero buys with no chance."""
    if mask.shape != (ACTIONS,) or not mask[executed]:
        raise ValueError("Unexpected/illegal action mask")
    t = turns.setdefault(turn, {
        "turn": turn, "decisions": 0, "legal_buy_decisions": 0,
        "selected_buys": 0, "model_end_while_buy_legal": 0,
        "forced_ends": 0, "proposed_end_turns": 0
    })
    buy_legal = bool(mask[8:16].any())
    t["decisions"] += 1
    summary["decisions"] += 1
    if buy_legal:
        t["legal_buy_decisions"] += 1
        summary["buy_legal_decisions"] += 1
    if 8 <= executed < 16:
        t["selected_buys"] += 1
        summary["selected_buys"] += 1
    if proposed == 0:
        t["proposed_end_turns"] += 1
        summary["model_proposed_ends"] += 1
    if proposed == 0 and buy_legal:
        t["model_end_while_buy_legal"] += 1
        summary["model_end_while_buy_legal"] += 1
    if forced:
        t["forced_ends"] += 1
        summary["guard_forced_ends"] += 1
    summary["proposed_action_kinds"][action_kind(proposed)] += 1
    summary["executed_action_kinds"][action_kind(executed)] += 1
    summary["raw_action_ids"][str(proposed)] += 1
    summary["max_identical_action_streak"] = max(summary["max_identical_action_streak"], streak)
    return streak


def trace(seed: int, policy: str, model_path: Path | None, guard_cap: int) -> tuple[dict, dict]:
    import taverngym

    engine = verify_engine()
    if guard_cap < 0:
        raise ValueError("guard_cap must be nonnegative")
    if policy == "model":
        if not model_path or not model_path.is_file():
            raise FileNotFoundError("A real model is required")
        from sb3_contrib import MaskablePPO
        model = MaskablePPO.load(str(model_path), device="cpu")
    elif policy == "baseline":
        model = None
    else:
        raise ValueError("policy must be model or baseline")

    game = taverngym.Game(seed=seed)
    baseline = BaselinePolicy()
    summary = {
        "decisions": 0, "buy_legal_decisions": 0, "selected_buys": 0,
        "model_proposed_ends": 0, "model_end_while_buy_legal": 0,
        "guard_forced_ends": 0, "max_identical_action_streak": 0,
        "proposed_action_kinds": Counter(), "executed_action_kinds": Counter(),
        "raw_action_ids": Counter()
    }
    turns: dict[int, dict] = {}
    last_turn = -1
    used = 0
    old_proposal: int | None = None
    streak = 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            used, old_proposal, streak, last_turn = 0, None, 0, turn
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(0)
            floats = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if floats.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned observe2/mask ABI mismatch")
            if model is None:
                proposed = int(baseline.act(
                    {"features": floats, "cards": cards, "action_mask": mask},
                    {"turn": turn, "actions_used": used}))
            else:
                proposed, _ = model.predict(
                    {"features": floats, "cards": cards},
                    action_masks=mask, deterministic=True)
                proposed = int(proposed)
            if not mask[proposed]:
                raise ValueError("Policy proposed illegal action")
            # Guard is explicit; model remains the proposer in the diagnostic.
            forced = policy == "model" and guard_cap > 0 and used >= guard_cap and mask[0] and proposed != 0
            executed = 0 if forced else proposed
            streak = streak + 1 if proposed == old_proposal else 1
            record_action(summary, turns, turn, mask, proposed, executed, bool(forced), streak)
            old_proposal = proposed
            game.step(0, executed)
            used += 1
        if not progressed and not game.is_over():
            raise RuntimeError("Game did not progress")
    if not game.is_over():
        raise RuntimeError("Full game safety limit exceeded (no receipt)")
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"], "agent_id": SESSION,
        "policy": policy, "seed": seed, "completed": True,
        "turns": int(game.turn), "decisions": summary["decisions"],
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest() if model_path else None
    }
    validate(receipt)
    summary["turns_with_legal_buy"] = sum(t["legal_buy_decisions"] > 0 for t in turns.values())
    summary["turns_with_selected_buy"] = sum(t["selected_buys"] > 0 for t in turns.values())
    report = {
        "schema": 1, "session_id": SESSION, "seed": seed,
        "policy": policy, "guard_cap": guard_cap,
        "performance_class": "guarded_model_not_raw" if policy == "model" and summary["guard_forced_ends"] else
                             ("raw_model" if policy == "model" else "baseline_with_internal_cap"),
        "model_release": RELEASE if policy == "model" else None,
        "engine": engine, "summary": dict(summary),
        "turns": [turns[k] for k in sorted(turns)],
        "receipt_placement": receipt["placements"][0],
        "interpretation": "Legal purchase opportunities are decision states, not proofs that a purchase was economically optimal. A guard-influenced result is not a raw model rank."
    }
    return receipt, report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--policy", choices=["baseline", "model"], required=True)
    ap.add_argument("--model", type=Path)
    ap.add_argument("--expected-sha256", default="")
    ap.add_argument("--guard-cap", type=int, default=0)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()
    if a.policy == "model":
        if not a.model or not a.model.is_file():
            ap.error("model file required")
        digest = hashlib.sha256(a.model.read_bytes()).hexdigest()
        if not a.expected_sha256 or digest != a.expected_sha256:
            raise ValueError("Model asset SHA256 does not match trusted expected digest")
    receipt, report = trace(a.seed, a.policy, a.model, a.guard_cap)
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    a.report.write_text(json.dumps(report, indent=2, default=dict) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(a.receipt), "report": str(a.report),
                      "rank": receipt["placements"][0], "summary": report["summary"]}, default=dict))


if __name__ == "__main__":
    main()
