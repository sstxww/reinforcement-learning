"""Raw PPO eight-seat gameplay with opportunity-conditioned legal-action telemetry.

No policy guard, state intervention, training, hidden player information or rank claims.
The only data recorded are the controlled seat's public observations/legal mask
and the final real TavernGym outcome.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION = "s-20261102-6b4eaf12"


def opportunity(mask, action: int) -> dict:
    m = np.asarray(mask, dtype=bool)
    if m.shape != (ACTIONS,) or not 0 <= action < ACTIONS or not m[action]:
        raise ValueError("Invalid legal action or action-mask shape")
    return {
        "buy_legal": bool(m[8:16].any()),
        "play_legal": bool(m[46:126].any()),
        "upgrade_legal": bool(m[3]),
        "buy_selected": 8 <= action < 16,
        "play_selected": 46 <= action < 126,
        "end_selected": action == 0,
    }


def run(seed: int, model_path: Path) -> tuple[dict, dict]:
    import taverngym
    from sb3_contrib import MaskablePPO

    engine = verify_engine()
    digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    counts: Counter[str] = Counter()
    by_turn: dict[int, Counter[str]] = {}
    total = 0
    this_turn = 0
    previous_turn = -1
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != previous_turn:
            previous_turn, this_turn = turn, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            fb, cb = game.observe2(0)
            features = np.frombuffer(fb, dtype="<f4").copy()
            cards = np.frombuffer(cb, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned observation dimensions changed")
            if not np.isfinite(features).all():
                raise ValueError("Non-finite controlled-seat observations")
            predicted, _ = model.predict(
                {"features": features, "cards": cards},
                action_masks=mask, deterministic=True,
            )
            action = int(np.asarray(predicted).item())
            flags = opportunity(mask, action)
            count = by_turn.setdefault(turn, Counter())
            count["decisions"] += 1
            for name, yes in flags.items():
                if yes:
                    counts[name] += 1
                    count[name] += 1
            if flags["buy_legal"] and flags["end_selected"]:
                counts["ended_with_legal_buy"] += 1
                count["ended_with_legal_buy"] += 1
            if flags["play_legal"] and flags["end_selected"]:
                counts["ended_with_legal_play"] += 1
                count["ended_with_legal_play"] += 1
            game.step(0, action)
            total += 1
            this_turn += 1
            if this_turn > 120:
                raise RuntimeError(f"Raw model exceeded 120 actions in turn {turn}; no forced END")
        if not progressed and not game.is_over():
            raise RuntimeError(f"Engine stalled in seed {seed}")
    if not game.is_over():
        raise RuntimeError("True full-game completion not reached")
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION, "policy": "raw_v2_model_no_guard",
        "seed": seed, "completed": True,
        "turns": int(game.turn), "decisions": total,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "model_sha256": digest, "guard_forced_ends": 0,
    }
    validate(receipt)
    if sorted(receipt["placements"]) != list(range(1, 9)):
        raise ValueError("Placements not eight distinct ranks")
    report = {
        "schema": 1, "experiment": "raw_model_legal_opportunities",
        "source_release": "v2-learning-41413557445",
        "model_sha256": digest, "seed": seed,
        "engine": engine,
        "counters": dict(sorted(counts.items())),
        "per_turn": [{"turn": t, **dict(sorted(c.items()))}
                     for t, c in sorted(by_turn.items())],
        "placement": receipt["placements"][0],
        "caution": "Single seed descriptive; mask opportunity is not proof that purchasing is strategically good.",
        "fresh_ppo_steps": 0, "fallback_guard": False,
    }
    return receipt, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=88132)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    receipt, report = run(args.seed, args.model)
    for path, data in ((args.receipt, receipt), (args.report, report)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"placement": report["placement"],
                      "seed": report["seed"],
                      "counters": report["counters"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
