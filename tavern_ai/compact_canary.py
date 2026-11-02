"""Session-owned genuine eight-seat model match with bounded repeated actions.

Uses the pinned TavernGym Game API. Does not alter the shared canary policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sb3_contrib import MaskablePPO

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

MAX_ACTIONS_PER_TURN = 80


def bounded_action(proposed: int, mask: np.ndarray, used: int) -> tuple[int, bool]:
    """End the turn before a poorly initialized model can loop indefinitely."""
    if mask.shape != (ACTIONS,) or not bool(mask.any()):
        raise ValueError("Unexpected or empty action mask")
    if used >= MAX_ACTIONS_PER_TURN and bool(mask[0]):
        return 0, True
    if proposed < 0 or proposed >= ACTIONS or not bool(mask[proposed]):
        raise ValueError(f"Illegal model action {proposed}")
    return proposed, False


def run(seed: int, agent_id: str, model_path: Path) -> dict:
    import taverngym

    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid agent id")
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    engine = verify_engine()
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    decisions = 0
    forced_end_turns = 0
    actions_this_turn = 0
    last_turn = -1
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            actions_this_turn = 0
            last_turn = turn
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
                (FEATURES,), (CARDS,), (ACTIONS,),
            ):
                raise ValueError("Unexpected TavernGym observe2 contract")
            if not bool(np.isfinite(features).all()):
                raise ValueError("Non-finite TavernGym features")
            proposed, _ = model.predict(
                {"features": features, "cards": cards},
                action_masks=mask, deterministic=True,
            )
            action, forced = bounded_action(
                int(proposed), mask, actions_this_turn
            )
            if not bool(mask[action]):
                raise ValueError("Illegal post-guard action")
            game.step(0, action)
            forced_end_turns += int(forced)
            actions_this_turn += 1
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("TavernGym match stalled")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")
    result = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id, "policy": "model",
        "policy_version": "session-bounded-maskableppo-v1",
        "seed": seed, "completed": True, "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "illegal_actions": 0,
        "max_actions_per_turn": MAX_ACTIONS_PER_TURN,
        "forced_end_turns": forced_end_turns,
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
    p.add_argument("--receipt", type=Path, required=True)
    a = p.parse_args()
    receipt = run(a.seed, a.agent_id, a.model)
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
