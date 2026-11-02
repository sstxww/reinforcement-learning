"""Experimental public-action only policy guard against Play -> Cancel loops.

This is NOT unmodified PPO. Explicitly mark all games as guarded candidates and
never use their record as a pure model receipt. Inference has no hidden state.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
from pathlib import Path

import numpy as np

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .release_integrity import sha256_file


def guard_mask(native: np.ndarray, prohibited: set[int]) -> np.ndarray:
    """Remove already-cancelled Play actions only when another legal move exists."""
    mask = np.asarray(native, dtype=bool).copy()
    if mask.shape != (ACTIONS,) or not mask.any():
        raise ValueError("Expected an intact nonempty legal native action mask")
    for action in sorted(prohibited):
        if 46 <= action < 126 and mask[action] and mask.sum() > 1:
            mask[action] = False
    if not mask.any() or np.any(mask & ~native):
        raise AssertionError("Guard must never create a new legal action")
    return mask


def update_cancel_blacklist(previous: int | None, chosen: int,
                            blocked: set[int]) -> bool:
    """An immediate Cancel(7) after Play marks the failed Play for this turn."""
    if chosen == 7 and previous is not None and 46 <= previous < 126:
        blocked.add(previous)
        return True
    return False


def play_one(seed: int, model_path: Path, expected_sha: str,
             *, max_decisions: int = 2000, max_per_turn: int = 300) -> dict:
    if sha256_file(model_path) != expected_sha:
        raise ValueError("Refuse to evaluate a different checkpoint")
    if not (1 <= max_decisions <= 3000 and 1 <= max_per_turn <= 500):
        raise ValueError("Invalid finite game bounds")
    engine = verify_engine()
    import taverngym
    from sb3_contrib import MaskablePPO

    learner = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    turn_now = None
    actions_this_turn = 0
    decisions = 0
    cancel_after_play = 0
    masked_decisions = 0
    removed_legal_play_count = 0
    legal_buy_opportunities = 0
    buy_actions = 0
    legal_buy_without_buy = 0
    observed_end_turns = 0
    original_actions = collections.Counter()
    blacklist: set[int] = set()
    blacklisted_this_game: set[int] = set()
    previous_action: int | None = None
    stop_reason = None
    for _ in range(30000):
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
            if turn != turn_now:
                turn_now = turn
                actions_this_turn = 0
                previous_action = None
                blacklist.clear()
            if decisions >= max_decisions:
                stop_reason = "controlled_decisions_bound"
                break
            if actions_this_turn >= max_per_turn:
                stop_reason = "per_turn_decisions_bound"
                break
            fbytes, cbytes = game.observe2(0)
            features = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            native_mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if (features.shape != (FEATURES,) or cards.shape != (CARDS,)
                or native_mask.shape != (ACTIONS,) or not native_mask.any()):
                raise RuntimeError("Observation contract or legal action mask corrupted")
            filtered = guard_mask(native_mask, blacklist)
            removed = int(np.count_nonzero(native_mask & ~filtered))
            masked_decisions += int(removed > 0)
            removed_legal_play_count += removed
            legal_buy = bool(native_mask[8:16].any())
            legal_buy_opportunities += int(legal_buy)
            action, _ = learner.predict(
                {"features": features, "cards": cards},
                action_masks=filtered, deterministic=True,
            )
            action = int(action)
            if not native_mask[action] or not filtered[action]:
                raise RuntimeError("Policy/guard requested an illegal action")
            if update_cancel_blacklist(previous_action, action, blacklist):
                cancel_after_play += 1
                blacklisted_this_game.update(blacklist)
            original_actions[action] += 1
            buy_actions += int(8 <= action < 16)
            legal_buy_without_buy += int(legal_buy and not 8 <= action < 16)
            observed_end_turns += int(action == 0)
            game.step(0, action)
            previous_action = action
            decisions += 1
            actions_this_turn += 1
        if stop_reason is not None:
            break
        if not progressed:
            stop_reason = "no_simulator_progress"
            break
    completed = bool(game.is_over())
    if not completed and stop_reason is None:
        stop_reason = "simulator_cycle_bound"
    return {
        "schema": 1,
        "experiment_type": "guarded_model_play_cancel_blacklist_not_pure_PPO",
        "model_sha256": expected_sha, "seed": seed, "engine": engine,
        "completed": completed, "failure_reason": None if completed else stop_reason,
        "policy_model_unchanged": True, "inference_action_mask_intervention": True,
        "best_or_champion_promoted": False,
        "model_controls_seat": 0, "opponents": "seven official TavernGym bots",
        "turns": int(game.turn), "decisions": decisions,
        "placements": [int(x) for x in game.placements()] if completed else None,
        "guarded_mask_decisions": masked_decisions,
        "total_removed_legally_available_play_indices": removed_legal_play_count,
        "cancel_immediately_after_play": cancel_after_play,
        "distinct_blacklisted_play_action_ids": sorted(blacklisted_this_game),
        "native_legal_buy_decisions": legal_buy_opportunities,
        "buy_actions": buy_actions,
        "decisions_with_legal_buy_but_no_buy": legal_buy_without_buy,
        "model_selected_end_turn_actions": observed_end_turns,
        "action_id_counts": {str(k): v for k, v in sorted(original_actions.items())},
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "comparison_note": (
            "Experimental changed-action-mask guarded policy, NOT unmodified PPO. "
            "A completed game is not a valid pure-model receipt. One or two games "
            "cannot establish competitive rank gains."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, type=Path)
    p.add_argument("--expected-sha", required=True)
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = play_one(args.seed, args.model, args.expected_sha)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
