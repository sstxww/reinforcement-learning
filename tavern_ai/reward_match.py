"""Session-isolated bounded model driver for genuine TavernGym 8-seat matches.

A near-untrained PPO can legally toggle optional actions forever. For an
honest comparison both experimental arms use the same per-turn fallback.
Every action still passes the simulator legal mask; seven seats run bots.
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .contract import FEATURES, CARDS, ACTIONS, verify_engine
from .validate_receipt import validate

MAX_ACTIONS_PER_TURN = 48


def bounded_action(mask: np.ndarray, proposed: int, used: int) -> tuple[int, bool]:
    """Return a legal move; with exhausted budget prefer ending the turn.

    In mandatory choice states ending is not legal, so take the first legal
    choice instead of stalling. The policy's normal choices are unchanged
    until MAX_ACTIONS_PER_TURN actions in the current turn.
    """
    valid = np.asarray(mask, dtype=bool)
    if valid.shape != (ACTIONS,) or not valid.any():
        raise ValueError("Malformed / empty action mask")
    if used >= MAX_ACTIONS_PER_TURN:
        if valid[0]:
            chosen = 0
        else:
            mandatory = np.flatnonzero(valid[30:46])
            chosen = int(mandatory[0] + 30) if len(mandatory) else int(np.flatnonzero(valid)[0])
    else:
        chosen = int(proposed)
        if chosen < 0 or chosen >= ACTIONS or not valid[chosen]:
            raise ValueError(f"Model emitted illegal action {chosen}")
    return chosen, chosen != int(proposed)


def run(seed: int, agent_id: str, policy: str = "model",
        model_path: str | None = None) -> dict:
    if policy != "model" or not model_path or not Path(model_path).is_file():
        raise ValueError("Session match requires a trained model.zip")
    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid agent ID")
    from sb3_contrib import MaskablePPO
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    model = MaskablePPO.load(model_path, device="cpu")
    decisions = 0
    overrides = 0
    last_turn = -1
    used_this_turn = 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, used_this_turn = turn, 0
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
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) \
                    or mask.shape != (ACTIONS,):
                raise ValueError("Pinned observe2 contract mismatch")
            proposal, _ = model.predict(
                {"features": features, "cards": cards},
                action_masks=mask, deterministic=True,
            )
            action, overridden = bounded_action(mask, int(proposal), used_this_turn)
            game.step(0, action)
            used_this_turn += 1
            decisions += 1
            overrides += int(overridden)
        if not progressed and not game.is_over():
            raise RuntimeError("TavernGym stalled without legal progress")
    if not game.is_over():
        raise RuntimeError("Model game exceeded 30000 scheduling rounds")
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": "model-bounded",
        "model_safety_limit": MAX_ACTIONS_PER_TURN,
        "model_safety_overrides": overrides,
        "seed": int(seed),
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(p) for p in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "model_sha256": hashlib.sha256(Path(model_path).read_bytes()).hexdigest(),
    }
    validate(result)
    return result
