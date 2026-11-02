"""Bounded real-game ablation: raw PPO argmax vs raw masked sampling.

This does NOT modify model weights or silently rescue model decisions. It records
completed genuine TavernGym games only; failures remain failures, not ranks.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from .buy_opportunity_68099929 import classify, summary_from_decisions
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .receipt_integrity import validate_integrity


def choose_raw_action(model, observation: dict, mask: np.ndarray, mode: str) -> int:
    """Call the model exactly once, without rule-policy substitution."""
    if mode not in ("argmax", "sampled"):
        raise ValueError("Unknown raw PPO selection mode")
    if mask.shape != (ACTIONS,) or mask.dtype != np.bool_ or not mask.any():
        raise ValueError("Invalid legal action mask")
    action, _ = model.predict(
        observation, action_masks=mask, deterministic=(mode == "argmax")
    )
    selected = int(np.asarray(action).item())
    if not 0 <= selected < ACTIONS or not mask[selected]:
        raise ValueError("Raw model chose an illegal action")
    return selected


def real_raw_game(checkpoint: Path, seed: int, agent_id: str, mode: str) -> dict:
    if mode not in ("argmax", "sampled"):
        raise ValueError("Unsupported selection mode")
    if not checkpoint.is_file() or not agent_id.startswith("s-") or "/" in agent_id:
        raise ValueError("Missing model or invalid agent identifier")

    import torch
    import taverngym
    from sb3_contrib import MaskablePPO

    engine = verify_engine()
    model_sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    model = MaskablePPO.load(str(checkpoint), device="cpu")
    # Deterministic policy is independent of this RNG; sampled policy has a
    # separately recorded deterministic CPU RNG initialization.
    sampling_seed = seed + 406
    torch.manual_seed(sampling_seed)
    np.random.seed(sampling_seed)

    game = taverngym.Game(seed=seed)
    last_turn, used_in_turn, decisions = -1, 0, 0
    prior_hash = None
    events: list[dict] = []
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, used_in_turn, prior_hash = turn, 0, None
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            f, c = game.observe2(0)
            features = np.frombuffer(f, dtype="<f4").copy()
            cards = np.frombuffer(c, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if (features.shape, cards.shape, mask.shape) != ((FEATURES,), (CARDS,), (ACTIONS,)):
                raise ValueError("Pinned engine observation/action contract mismatch")
            if not np.isfinite(features).all():
                raise ValueError("Nonfinite public observation")
            public_hash = hashlib.sha256(
                features.tobytes() + cards.tobytes() + mask.tobytes()
            ).hexdigest()[:24]
            action = choose_raw_action(
                model, {"features": features, "cards": cards}, mask, mode
            )
            events.append({
                "turn": turn, "action": action, "family": classify(action),
                "buy_legal": bool(mask[8:16].any()),
                "legal_buy_count": int(mask[8:16].sum()),
                "board_size": int(round(float(features[33]))),
                "state_hash": public_hash,
                "same_public_state_as_prior": public_hash == prior_hash,
            })
            game.step(0, action)
            decisions += 1
            used_in_turn += 1
            prior_hash = public_hash
            if used_in_turn > 250:
                raise RuntimeError("Raw PPO decision limit; NO completed ranking")
        if not progressed and not game.is_over():
            raise RuntimeError("Actual engine stalled; NO completed ranking")
    if not game.is_over():
        raise RuntimeError("Actual eight-seat match unfinished; NO completed ranking")

    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": agent_id, "seed": seed, "policy": "model",
        "model_sha256": model_sha, "selection_mode": mode,
        "sampling_seed": sampling_seed if mode == "sampled" else None,
        "completed": True, "turns": int(game.turn), "decisions": decisions,
        "placements": [int(p) for p in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "opportunity_summary": summary_from_decisions(events),
        "trace_first_32": events[:32],
        "fallback_actions": 0, "guard_forced_ends": 0,
        "model_guard_forced_end": 0,
        "public_observation_only": True,
        "purpose": "single-seed selection ablation; no strength or promotion claim",
    }
    validate_integrity(receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--mode", choices=("argmax", "sampled"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = real_raw_game(args.model, args.seed, args.agent_id, args.mode)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "seed": args.seed, "mode": args.mode,
        "rank": receipt["placements"][0],
        "model_sha256": receipt["model_sha256"],
        "opportunity_summary": receipt["opportunity_summary"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
