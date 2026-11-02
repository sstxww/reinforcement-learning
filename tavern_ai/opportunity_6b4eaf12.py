"""Genuine V2 PPO behavior: raw-loop abort and separately-labelled guarded full game.

The controlled seat sees only observe2 public features/cards and its legal mask.
No hidden opponent state, no fake full match, no retraining. Raw loops are
reported as INCOMPLETE, not as losses/ranks. Guarded results disclose forced END.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION = "s-20261102-6b4eaf12"
RAW_ACTION_LIMIT = 120


def opportunity(mask, action: int) -> dict:
    m = np.asarray(mask, dtype=bool)
    if m.shape != (ACTIONS,) or not 0 <= action < ACTIONS or not m[action]:
        raise ValueError("Invalid legal action or action-mask shape")
    return {
        "buy_legal": bool(m[8:16].any()),
        "play_legal": bool(m[46:126].any()),
        "upgrade_legal": bool(m[3]),
        "buy_selected": 8 <= action < 16,
        "play_selected": 46 <= action < 126,
        "end_selected": action == 0,
    }


def _per_turn(by_turn: dict[int, Counter[str]]) -> list[dict]:
    return [{"turn": t, **dict(sorted(c.items()))}
            for t, c in sorted(by_turn.items())]


def run(seed: int, model_path: Path, *, guard_budget: int | None = None) -> tuple[dict | None, dict]:
    """Raw: stop at 120 actions/turn and save an incomplete trace.
    Guarded: legally force END at the given per-turn budget and play to game over.
    """
    import taverngym
    from sb3_contrib import MaskablePPO

    if guard_budget is not None and not (1 <= guard_budget <= 100):
        raise ValueError("guard_budget must be 1..100")
    engine = verify_engine()
    digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    counts: Counter[str] = Counter()
    by_turn: dict[int, Counter[str]] = {}
    total = 0
    this_turn = 0
    previous_turn = -1
    forced = 0
    last_action: int | None = None
    streak = 0
    highest_streak = 0
    first_actions: list[int] = []

    def report(*, completed: bool, failure: str | None = None,
               placement: int | None = None) -> dict:
        return {
            "schema": 1,
            "experiment": "ppo_legal_opportunities_and_action_loop",
            "source_release": "v2-learning-41413557445",
            "model_sha256": digest, "seed": seed,
            "engine": engine, "completed": completed,
            "policy": "raw_no_intervention" if guard_budget is None
                      else "guarded_budget_end_turn",
            "guard_budget": guard_budget,
            "guard_forced_ends": forced,
            "decision_count": total,
            "model_selected_end_turns": counts["end_selected"],
            "counters": dict(sorted(counts.items())),
            "per_turn": _per_turn(by_turn),
            "first_actions": first_actions,
            "max_consecutive_identical_actions": highest_streak,
            "failure": failure, "placement": placement,
            "caution": (
                "Raw early-abort is NOT a complete match and has no valid placement. "
                "Guarded completion is not equivalent to raw policy strength. "
                "Legal BUY opportunity is not proof buying was strategically good."
            ),
            "fresh_ppo_steps": 0,
        }

    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != previous_turn:
            previous_turn, this_turn = turn, 0
            last_action, streak = None, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            if this_turn >= RAW_ACTION_LIMIT:
                # Do not falsely claim completion. The real engine did not end.
                return None, report(
                    completed=False,
                    failure=f"model action loop: turn {turn} reached {this_turn} raw decisions"
                )
            fb, cb = game.observe2(0)
            features = np.frombuffer(fb, dtype="<f4").copy()
            cards = np.frombuffer(cb, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned observation dimensions changed")
            if not np.isfinite(features).all():
                raise ValueError("Non-finite controlled-seat observations")
            guarded = bool(guard_budget is not None and this_turn >= guard_budget and mask[0])
            if guarded:
                action = 0
                forced += 1
            else:
                predicted, _ = model.predict(
                    {"features": features, "cards": cards},
                    action_masks=mask, deterministic=True,
                )
                action = int(np.asarray(predicted).item())
            flags = opportunity(mask, action)
            count = by_turn.setdefault(turn, Counter())
            count["decisions"] += 1
            count[f"action_id_{action}"] += 1
            counts[f"action_id_{action}"] += 1
            if guarded:
                counts["forced_end"] += 1
                count["forced_end"] += 1
            for name, yes in flags.items():
                if yes:
                    counts[name] += 1
                    count[name] += 1
            if flags["end_selected"] and not guarded:
                counts["model_natural_end"] += 1
                count["model_natural_end"] += 1
            if flags["buy_legal"] and flags["end_selected"]:
                counts["ended_with_legal_buy"] += 1
                count["ended_with_legal_buy"] += 1
            if flags["play_legal"] and flags["end_selected"]:
                counts["ended_with_legal_play"] += 1
                count["ended_with_legal_play"] += 1
            streak = streak + 1 if action == last_action else 1
            highest_streak = max(highest_streak, streak)
            last_action = action
            if len(first_actions) < 35:
                first_actions.append(action)
            before = hashlib.sha256(features.tobytes() + cards.tobytes() + mask.tobytes()).digest()
            game.step(0, action)
            if game.needs_action(0):
                after_fb, after_cb = game.observe2(0)
                after_mask = game.legal_mask(0)
                after = hashlib.sha256(after_fb + after_cb + after_mask).digest()
                if after == before:
                    counts["same_public_state_after_action"] += 1
                    count["same_public_state_after_action"] += 1
            total += 1
            this_turn += 1
        if not progressed and not game.is_over():
            raise RuntimeError(f"Engine stalled in seed {seed}")
    if not game.is_over():
        return None, report(completed=False, failure="30000-iteration game safety stop")
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION,
        "policy": ("raw_v2_model_no_guard" if guard_budget is None else
                   f"guarded_v2_end_turn_budget_{guard_budget}"),
        "seed": seed, "completed": True,
        "turns": int(game.turn), "decisions": total,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "model_sha256": digest, "guard_forced_ends": forced,
    }
    validate(receipt)
    if sorted(receipt["placements"]) != list(range(1, 9)):
        raise ValueError("Placements not eight distinct ranks")
    return receipt, report(completed=True, placement=receipt["placements"][0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=88132)
    parser.add_argument("--guard-budget", type=int)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    receipt, result = run(args.seed, args.model, guard_budget=args.guard_budget)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if receipt is not None:
        if args.receipt is None:
            parser.error("--receipt is required if a genuine full game completed")
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    elif args.receipt is not None:
        # Fail closed, never write a fake receipt.
        raise RuntimeError("Incomplete real match; diagnostic report saved, no receipt emitted")
    print(json.dumps({
        "completed": result["completed"], "seed": result["seed"],
        "placement": result["placement"], "failure": result["failure"],
        "guard_forced_ends": result["guard_forced_ends"],
        "counters": result["counters"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
