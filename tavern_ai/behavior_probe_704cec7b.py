"""Evidence-only V2 PPO action diagnostics with explicit guard accounting.

The model only sees public observe2 fields and the legal action mask.
A forced end is never counted as a model choice. Public-state equivalence
is not proof of a game-engine no-op.
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

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

TURN_BUDGET = 40


def action_category(action: int) -> str:
    if action == 0:
        return "END_TURN"
    if action == 3:
        return "UPGRADE"
    if 8 <= action <= 15:
        return "BUY"
    if 16 <= action <= 22:
        return "SELL"
    if 23 <= action <= 29:
        return "REFRESH_OR_FREEZE"
    if 30 <= action <= 45:
        return "CHOICE"
    if 46 <= action <= 125:
        return "PLAY"
    if 126 <= action <= 195:
        return "MAGNETIZE"
    return "OTHER"


def summarize(events: list[dict]) -> dict:
    categories = Counter()
    legal_buy = 0
    end_with_legal_buy = 0
    ended_turn_with_buy = set()
    had_buy_in_turn = set()
    selected_buys = 0
    forced_end = 0
    observed_unchanged = 0
    repeats = 0
    last_by_turn: dict[int, int] = {}
    per_turn = {}
    for row in events:
        action = row["action"]
        turn = row["turn"]
        categories[action_category(action)] += 1
        if row["buy_legal"]:
            legal_buy += 1
            had_buy_in_turn.add(turn)
        if action == 0 and row["buy_legal"]:
            end_with_legal_buy += 1
            ended_turn_with_buy.add(turn)
        if 8 <= action <= 15:
            selected_buys += 1
        if row["forced_end"]:
            forced_end += 1
        if row.get("public_observation_unchanged") is True:
            observed_unchanged += 1
        if last_by_turn.get(turn) == action:
            repeats += 1
        last_by_turn[turn] = action
        state = per_turn.setdefault(str(turn), {"decisions": 0, "buys": 0,
                                                "buy_legal_seen": False,
                                                "model_ends": 0, "forced_ends": 0})
        state["decisions"] += 1
        state["buys"] += int(8 <= action <= 15)
        state["buy_legal_seen"] |= bool(row["buy_legal"])
        state["model_ends"] += int(action == 0 and not row["forced_end"])
        state["forced_ends"] += int(row["forced_end"])
    return {
        "model_actions": len(events) - forced_end,
        "total_controlled_actions": len(events),
        "action_counts": dict(categories),
        "buy_legal_decision_states": legal_buy,
        "turns_with_any_legal_buy": len(had_buy_in_turn),
        "selected_buys": selected_buys,
        "end_turn_while_buy_legal": end_with_legal_buy,
        "turns_ended_with_buy_legal": len(ended_turn_with_buy),
        "guard_forced_end_turns": forced_end,
        "same_action_adjacent_within_turn": repeats,
        "observable_unchanged_post_actions": observed_unchanged,
        "per_turn": per_turn,
        "opportunity_note": "Mask[8:16] is a legal-buy signal, not proof of a high-value purchase.",
        "unchanged_note": "Equal observable state is not proof of zero hidden-state change.",
    }


def run(seed: int, model_path: Path, expected_sha256: str) -> dict:
    import taverngym
    from sb3_contrib import MaskablePPO

    h = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if h != expected_sha256:
        raise ValueError("Checkpoint hash mismatch")
    engine = verify_engine()
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    if game.num_players != 8:
        raise RuntimeError("Expected eight-seat game")
    events = []
    current_turn = -1
    used = 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != current_turn:
            current_turn, used = turn, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat:
                game.bot_play(seat)
                continue
            fb, cb = game.observe2(0)
            features = np.frombuffer(fb, dtype="<f4").copy()
            cards = np.frombuffer(cb, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if (features.shape != (FEATURES,) or cards.shape != (CARDS,)
                    or mask.shape != (ACTIONS,) or not np.isfinite(features).all()):
                raise ValueError("Public observation / mask mismatch")
            before = hashlib.sha256(features.tobytes() + cards.tobytes() + mask.tobytes()).hexdigest()
            forced = used >= TURN_BUDGET
            if forced:
                if not mask[0]:
                    raise RuntimeError("No legal end turn at budget")
                action = 0
            else:
                proposal, _ = model.predict({"features": features, "cards": cards},
                                            action_masks=mask, deterministic=True)
                action = int(np.asarray(proposal).item())
            if action < 0 or action >= ACTIONS or not mask[action]:
                raise RuntimeError("Model/guard produced illegal action")
            event = {
                "turn": turn, "action": action,
                "forced_end": forced,
                "buy_legal": bool(mask[8:16].any()),
                "board_size_observed": float(features[33]),
                "hand_size_observed": float(features[34]),
                "public_observation_unchanged": None,
            }
            game.step(0, action)
            used += 1
            if action != 0 and game.needs_action(0):
                next_fb, next_cb = game.observe2(0)
                next_mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8)
                after = hashlib.sha256(next_fb + next_cb + next_mask.tobytes()).hexdigest()
                event["public_observation_unchanged"] = before == after
            events.append(event)
        if not progressed and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Real match safety limit exceeded")
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": "s-20261102-704cec7b",
        "policy": "guarded_model_diagnostic_not_raw",
        "seed": seed, "completed": True,
        "turns": int(game.turn),
        "decisions": len(events),
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "model_sha256": h,
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "diagnostics": summarize(events),
        "all_action_events": events,
        "promotion_eligible": False,
    }
    validate(result)
    if sorted(result["placements"]) != list(range(1, 9)):
        raise ValueError("Placements are not an eight-seat permutation")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, type=Path)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--receipt", required=True, type=Path)
    args = p.parse_args()
    result = run(args.seed, args.model, args.expected_sha256)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    print(json.dumps({"seed": result["seed"], "rank": result["placements"][0],
                      "diagnostics": result["diagnostics"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
