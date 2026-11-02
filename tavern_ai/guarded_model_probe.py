"""Isolated PPO turn-budget experiment; no production policy edits."""
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

def choose_guarded(mask, proposed, actions_this_turn, budget):
    mask = np.asarray(mask, dtype=bool)
    if mask.shape != (ACTIONS,) or not mask.any():
        raise ValueError("Expected nonempty 245-action mask")
    if budget < 1 or actions_this_turn < 0:
        raise ValueError("Invalid turn budget")
    proposed = int(proposed)
    if not (0 <= proposed < ACTIONS and mask[proposed]):
        raise ValueError(f"Model proposed illegal action: {proposed}")
    if actions_this_turn >= budget and mask[0] and proposed != 0:
        return 0, True
    return proposed, False

def run(seed: int, agent_id: str, model_path: Path, budget: int = 32):
    import taverngym
    from sb3_contrib import MaskablePPO
    if not agent_id or any(c in agent_id for c in "/\\"):
        raise ValueError("Invalid agent id")
    if budget < 1:
        raise ValueError("Invalid turn budget")
    engine = verify_engine()
    model_sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    decisions = 0
    forced_ends = 0
    max_actions = 0
    last_turn = -1
    actions_this_turn = 0
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
            if seat:
                game.bot_play(seat)
                continue
            floats, card_bytes = game.observe2(0)
            features = np.frombuffer(floats, dtype="<f4").copy()
            cards = np.frombuffer(card_bytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Incompatible observation")
            if not np.isfinite(features).all():
                raise ValueError("Nonfinite observation")
            proposal, _ = model.predict({"features":features,"cards":cards}, action_masks=mask, deterministic=True)
            action, forced = choose_guarded(mask, int(proposal), actions_this_turn, budget)
            game.step(0, action)
            decisions += 1
            forced_ends += int(forced)
            actions_this_turn += 1
            max_actions = max(max_actions, actions_this_turn)
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled without pending actions")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"], "engine_version": engine["version"],
        "agent_id": agent_id, "policy": "model_guarded", "seed": seed,
        "completed": True, "turns": int(game.turn), "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": model_sha, "model_timesteps": int(model.num_timesteps),
        "guard_max_turn_actions": budget, "guard_interventions": forced_ends,
        "observed_max_actions_per_turn": max_actions
    }
    validate(receipt)
    return receipt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--max-turn-actions", type=int, default=32)
    parser.add_argument("--receipt", required=True, type=Path)
    a = parser.parse_args()
    receipt = run(a.seed, a.agent_id, a.model, a.max_turn_actions)
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print("RECEIPT_JSON=" + json.dumps(receipt, separators=(",", ":")))

if __name__ == "__main__":
    main()
