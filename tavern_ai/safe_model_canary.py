"""Session-isolated guarded inference for genuine full TavernGym games.

The raw 128-step PPO policy can endlessly execute valid shop actions without
ending a turn. This policy delegates decisions to the learned model until a
fixed per-turn cap, then selects the legally masked end-turn action (index 0).
This safety intervention is reported explicitly, never disguised as pure PPO.
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


def choose_action(model, obs: dict, mask: np.ndarray, used: int, cap: int = 64):
    mask = np.asarray(mask, dtype=bool)
    if mask.shape != (ACTIONS,) or not mask.any():
        raise ValueError("Invalid or empty legal action mask")
    if used >= cap and mask[0]:
        return 0, True
    choice, _ = model.predict(obs, action_masks=mask, deterministic=True)
    action = int(np.asarray(choice).item())
    if action < 0 or action >= ACTIONS or not mask[action]:
        raise ValueError(f"Illegal masked model action: {action}")
    return action, False


def run(seed: int, agent_id: str, model_path: Path, cap: int = 64):
    import taverngym
    from sb3_contrib import MaskablePPO

    if not agent_id or any(c in agent_id for c in ("/", "\\")):
        raise ValueError("Invalid agent id")
    if cap < 1 or cap > 512:
        raise ValueError("Unsafe action cap")
    model_path = Path(model_path)
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    engine = verify_engine()
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    decisions = 0
    forced_end_turns = 0
    last_turn = -1
    actions_this_turn = 0
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
            fbytes, cbytes = game.observe2(0)
            f = np.frombuffer(fbytes, dtype="<f4").copy()
            c = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,):
                raise ValueError("Unexpected observation contract")
            action, forced = choose_action(
                model, {"features": f, "cards": c}, mask,
                actions_this_turn, cap=cap,
            )
            game.step(0, action)
            decisions += 1
            actions_this_turn += 1
            forced_end_turns += int(forced)
        if not progressed and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded despite end-turn cap")
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": "model-with-legal-end-turn-cap",
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
        "end_turn_cap": cap,
        "forced_end_turns": forced_end_turns,
    }
    validate(result)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--agent-id", required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--cap", type=int, default=64)
    p.add_argument("--receipt", type=Path, required=True)
    a = p.parse_args()
    result = run(a.seed, a.agent_id, a.model, a.cap)
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
