"""Private full-game runner with a legal per-turn action budget for PPO.

The public V1 canary's raw model action selection can loop forever on free
actions. This experiment only adds a mask-checked end-turn override.  It does
not modify the shared canary or the simulator.
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

MAX_ACTIONS_PER_TURN = 40
MAX_GAME_ITERATIONS = 30000


def run(seed: int, agent_id: str, policy: str = "model",
        model_path: str | None = None) -> dict:
    import taverngym
    from sb3_contrib import MaskablePPO

    if policy != "model":
        raise ValueError("This independent runner supports model policy only")
    if not agent_id.startswith("s-") or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid session identity")
    if not model_path or not Path(model_path).is_file():
        raise FileNotFoundError(model_path)
    engine = verify_engine()
    model = MaskablePPO.load(model_path, device="cpu")
    fallback = BaselinePolicy()
    game = taverngym.Game(seed=seed)
    turns_seen = -1
    actions_this_turn = 0
    decisions = 0
    forced_ends = 0
    emergency_choices = 0

    for _ in range(MAX_GAME_ITERATIONS):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != turns_seen:
            turns_seen = turn
            actions_this_turn = 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue

            fbytes, cbytes = game.observe2(0)
            features = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if (features.shape != (FEATURES,) or cards.shape != (CARDS,)
                    or mask.shape != (ACTIONS,) or not mask.any()
                    or not np.isfinite(features).all()):
                raise RuntimeError("Simulator observation/mask contract failed")

            if actions_this_turn >= MAX_ACTIONS_PER_TURN and mask[0]:
                action = 0
                forced_ends += 1
            elif actions_this_turn >= MAX_ACTIONS_PER_TURN:
                action = fallback.act(
                    {"features": features, "cards": cards, "action_mask": mask},
                    {"turn": turn, "actions_used": actions_this_turn},
                )
                emergency_choices += 1
            else:
                action, _ = model.predict(
                    {"features": features, "cards": cards},
                    action_masks=mask, deterministic=True,
                )
                action = int(action)
            if action < 0 or action >= ACTIONS or not mask[action]:
                raise ValueError("Masked policy selected an illegal action")

            game.step(0, int(action))
            actions_this_turn += 1
            decisions += 1
        if not progressed and not game.is_over():
            raise RuntimeError("Real eight-seat game stalled")

    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded despite action budget")
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": "maskable_ppo_with_40_action_turn_budget",
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "per_turn_action_cap": MAX_ACTIONS_PER_TURN,
        "forced_end_turns": forced_ends,
        "mandatory_fallback_choices": emergency_choices,
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": hashlib.sha256(Path(model_path).read_bytes()).hexdigest(),
    }
    validate(result)
    return result
