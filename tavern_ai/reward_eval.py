"""Isolated evaluation of a PPO seat with transparent legal end-turn protection.

The stock canary remains untouched. This evaluation is a different, guarded policy:
never report it as an evaluation of the raw PPO without interventions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate


def choose_action(model, observation: dict, mask: np.ndarray, used: int, max_actions: int):
    if max_actions < 1:
        raise ValueError("max_actions must be >=1")
    if mask.shape != (ACTIONS,) or not mask.any():
        raise ValueError("Invalid or empty action mask")
    if used >= max_actions and bool(mask[0]):
        return 0, True
    action, _ = model.predict(
        observation, action_masks=mask, deterministic=True
    )
    action = int(action)
    if not 0 <= action < ACTIONS or not mask[action]:
        raise ValueError(f"Model selected illegal action: {action}")
    return action, False


def run(seed: int, agent_id: str, model_path: Path, max_actions: int = 18) -> dict:
    import taverngym
    from sb3_contrib import MaskablePPO

    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid agent id")
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    engine = verify_engine()
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    decisions, guarded_ends, actions_this_turn, last_turn = 0, 0, 0, -1
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
            if seat != 0:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(0)
            features = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if (features.shape, cards.shape, mask.shape) != (
                (FEATURES,), (CARDS,), (ACTIONS,)
            ):
                raise ValueError("Unexpected observe2 contract")
            if not np.isfinite(features).all():
                raise ValueError("Non-finite observation features")
            action, guarded = choose_action(
                model, {"features": features, "cards": cards},
                mask, actions_this_turn, max_actions
            )
            game.step(0, action)
            guarded_ends += int(guarded)
            decisions += 1
            actions_this_turn += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Guarded full-game safety limit exceeded")
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": "model_guarded",
        "policy_version": "reward-study-v1-end-turn-cap",
        "max_actions_per_turn": max_actions,
        "guarded_ends": guarded_ends,
        "illegal_actions": 0,
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
    }
    validate(result)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--agent-id", required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--max-actions-per-turn", type=int, default=18)
    p.add_argument("--receipt", type=Path, required=True)
    a = p.parse_args()
    receipt = run(a.seed, a.agent_id, a.model, a.max_actions_per_turn)
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
