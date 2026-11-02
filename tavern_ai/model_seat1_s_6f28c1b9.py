"""Strict raw-model, nonzero-seat TavernGym evaluation. No baseline fallback."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import traceback

import numpy as np
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .receipt_integrity import validate_integrity

EXPECTED_MODEL_SHA256 = "a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632"
MODEL_RELEASE_TAG = "v5-s-20261102-68099929-1408-41428692617"

def play(seed: int, seat: int, agent_id: str, checkpoint: Path,
         *, model_loader=None, game_factory=None, max_decisions: int = 1800) -> dict:
    if type(seed) is not int or seed < 0:
        raise ValueError("invalid seed")
    if type(seat) is not int or not 0 <= seat <= 7:
        raise ValueError("invalid seat")
    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("invalid agent id")
    if type(max_decisions) is not int or not 1 <= max_decisions <= 6000:
        raise ValueError("invalid finite decision budget")
    checkpoint = Path(checkpoint)
    if not checkpoint.is_file():
        raise FileNotFoundError(str(checkpoint))
    model_sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    if model_sha != EXPECTED_MODEL_SHA256 and model_loader is None:
        raise ValueError("Official release checkpoint SHA256 mismatch")
    engine = verify_engine()
    if game_factory is None:
        import taverngym
        game_factory = lambda x: taverngym.Game(seed=x)
    if model_loader is None:
        from sb3_contrib import MaskablePPO
        model_loader = MaskablePPO.load
    model = model_loader(str(checkpoint), device="cpu")
    game = game_factory(seed)
    if game.num_players != 8:
        raise RuntimeError("Not an eight-seat game")
    decisions = 0
    counts = Counter()
    last_action = None
    streak = longest_streak = 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        progress = False
        for current in range(game.num_players):
            if not game.needs_action(current):
                continue
            progress = True
            if current != seat:
                game.bot_play(current)
                continue
            if decisions >= max_decisions:
                raise RuntimeError(
                    f"Raw PPO decision safety limit exceeded: seed={seed} "
                    f"seat={seat} decisions={decisions} turn={turn}; no placement")
            fb, cb = game.observe2(seat)
            features = np.frombuffer(fb, dtype="<f4").copy()
            cards = np.frombuffer(cb, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(seat), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise RuntimeError("Pinned observe2 dimensions changed")
            if not np.isfinite(features).all() or not mask.any():
                raise RuntimeError("Nonfinite observation or empty action mask")
            action, _ = model.predict({"features": features, "cards": cards},
                                      action_masks=mask, deterministic=True)
            action = int(np.asarray(action).item())
            if action < 0 or action >= ACTIONS or not mask[action]:
                raise RuntimeError(f"Model selected illegal raw action: {action}")
            game.step(seat, action)  # Truly raw; NEVER replace with baseline or forced action.
            decisions += 1
            counts[action] += 1
            streak = streak + 1 if action == last_action else 1
            longest_streak = max(longest_streak, streak)
            last_action = action
        if not progress and not game.is_over():
            raise RuntimeError(f"Stalled game: seed={seed} seat={seat} turn={turn}")
    if not game.is_over():
        raise RuntimeError(f"Raw game safety limit exceeded: seed={seed} seat={seat}; no placement")
    places = [int(x) for x in game.placements()]
    run_id = os.environ.get("GITHUB_RUN_ID")
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"], "agent_id": agent_id,
        "policy": "model", "evaluation_method": "v7-raw-nonzero-seat",
        "seat": seat, "controlled_seat": seat, "agent_placement": places[seat],
        "model_release_tag": MODEL_RELEASE_TAG, "model_sha256": model_sha,
        "seed": seed, "completed": True, "turns": int(game.turn),
        "decisions": decisions, "placements": places,
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "fallback_actions": 0, "guard_forced_ends": 0, "assisted_actions": 0,
        "raw_action_histogram": {str(k): v for k, v in sorted(counts.items())},
        "longest_identical_raw_action_streak": longest_streak,
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "workflow_run_url": (
            f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{run_id}"
            if run_id and os.environ.get("GITHUB_REPOSITORY") else None),
    }
    validate_integrity(receipt)
    return receipt

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--seat", type=int, default=1)
    p.add_argument("--agent-id", required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--failure", type=Path, required=True)
    args = p.parse_args()
    try:
        result = play(args.seed, args.seat, args.agent_id, args.checkpoint)
    except Exception as exc:
        args.failure.parent.mkdir(parents=True, exist_ok=True)
        args.failure.write_text(json.dumps({
            "completed": False, "placement": None, "policy": "model",
            "guarded": False, "seed": args.seed, "seat": args.seat,
            "model_release_tag": MODEL_RELEASE_TAG,
            "model_sha256_expected": EXPECTED_MODEL_SHA256,
            "error_type": type(exc).__name__, "failure_signature": str(exc),
            "traceback": traceback.format_exc(limit=5),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "git_sha": os.environ.get("GITHUB_SHA"),
        }, indent=2) + "\n", encoding="utf-8")
        raise
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"completed": True, "seed": args.seed, "seat": args.seat,
                       "placement": result["agent_placement"], "decisions": result["decisions"],
                       "model_sha256": result["model_sha256"]}), flush=True)

if __name__ == "__main__":
    main()
