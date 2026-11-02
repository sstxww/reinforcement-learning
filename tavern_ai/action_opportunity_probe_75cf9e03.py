"""Trace legal BUY opportunities and no-progress behavior in real TavernGym.

The optional legal END_TURN escape is ALWAYS disclosed. A guard-assisted
complete game is NOT a model-only competitive result or Champion evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from .contract import ACTIONS, CARDS, FEATURES, verify_engine


def trace(seed: int, model_path: Path, max_per_turn: int = 40) -> dict:
    if not 1 <= max_per_turn <= 100:
        raise ValueError("max_per_turn must be 1..100")
    import taverngym
    from sb3_contrib import MaskablePPO
    engine = verify_engine()
    model_path = Path(model_path)
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=int(seed))
    last_turn = -1
    actions_this_turn = 0
    model_actions = 0
    buy_available_decisions = 0
    buy_while_legal = 0
    end_when_buy_legal = 0
    model_chosen_ends = 0
    forced_end = 0
    play_count = 0
    buy_count = 0
    unchanged_public_state = 0
    other_actions = 0
    max_identical_streak = 0
    last_model_action = None
    identical_streak = 0
    forced_end_turns = []
    examples = []
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, actions_this_turn = turn, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            feature_bytes, card_bytes = game.observe2(0)
            features = np.frombuffer(feature_bytes, dtype="<f4").copy()
            cards = np.frombuffer(card_bytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned observation or action contract mismatch")
            buy_legal = bool(mask[8:16].any())
            if buy_legal:
                buy_available_decisions += 1
            selected, _ = model.predict({"features": features, "cards": cards},
                                        action_masks=mask, deterministic=True)
            action = int(selected)
            if action < 0 or action >= ACTIONS or not mask[action]:
                raise RuntimeError("Model selected an illegal action")
            forced = actions_this_turn >= max_per_turn
            if forced:
                if not mask[0]:
                    raise RuntimeError("Cannot safely end an exhausted turn")
                action = 0
                forced_end += 1
                forced_end_turns.append(turn)
            else:
                model_actions += 1
                if action == 0:
                    model_chosen_ends += 1
                if buy_legal and action == 0:
                    end_when_buy_legal += 1
                if action == last_model_action:
                    identical_streak += 1
                else:
                    identical_streak = 1
                    last_model_action = action
                max_identical_streak = max(max_identical_streak, identical_streak)
            if 8 <= action < 16:
                buy_count += 1
                if buy_legal:
                    buy_while_legal += 1
            elif 46 <= action < 126:
                play_count += 1
            elif action != 0:
                other_actions += 1
            game.step(0, action)
            if not forced and action != 0 and game.needs_action(0):
                af, ac = game.observe2(0)
                if af == feature_bytes and ac == card_bytes:
                    unchanged_public_state += 1
            if len(examples) < 16 and (forced or buy_legal and action == 0):
                examples.append({"turn":turn, "action":action, "legal_buy":buy_legal,
                                 "forced_end":forced, "decisions_this_turn":actions_this_turn})
            actions_this_turn += 1
        if not progressed and not game.is_over():
            raise RuntimeError("TavernGym stalled during guarded action trace")
    if not game.is_over():
        raise RuntimeError("Guarded game also exceeded full-game safety limit")
    return {
        "schema": 1, "session_id": "s-20261102-75cf9e03",
        "experiment": "guarded_model_action_opportunity_diagnostic",
        "environment": "TavernGym", "engine": engine, "seed": int(seed),
        "model_sha256": digest, "model_only_game": forced_end == 0,
        "guarded_model": forced_end > 0,
        "completed": True, "turns": int(game.turn),
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "max_actions_per_turn": max_per_turn,
        "model_chosen_actions": model_actions,
        "model_chosen_ends": model_chosen_ends,
        "guard_forced_ends": forced_end,
        "forced_end_turns": forced_end_turns[:60],
        "legal_buy_opportunity_decisions": buy_available_decisions,
        "model_end_when_buy_legal": end_when_buy_legal,
        "buy_actions": buy_count, "buy_actions_when_buy_legal": buy_while_legal,
        "play_actions": play_count, "other_actions": other_actions,
        "unchanged_public_state_actions": unchanged_public_state,
        "longest_identical_model_action_streak": max_identical_streak,
        "examples": examples,
        "promoted_champion": False,
        "inference": "guard-assisted diagnostic, no competitive strength claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=65811)
    parser.add_argument("--max-per-turn", type=int, default=40)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = trace(args.seed, args.model, args.max_per_turn)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
