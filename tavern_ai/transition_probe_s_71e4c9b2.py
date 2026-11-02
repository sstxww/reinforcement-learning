"""Bounded public-observation transition probe for an unchanged PPO checkpoint.

No intervention or fallback. A state hash is a view of public observe2 and
legal-mask bytes, NOT the simulator's full state; skipped poststates are not
counted as unchanged. Incomplete games never become match receipts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def action_family(action: int) -> str:
    if type(action) is not int or not 0 <= action < 245:
        raise ValueError("Invalid pinned action ID")
    families = (
        ("end", 0, 1), ("refresh", 1, 2), ("freeze", 2, 3),
        ("upgrade", 3, 4), ("hero_power", 4, 6), ("dark_gift", 6, 7),
        ("cancel", 7, 8), ("buy", 8, 16), ("sell", 16, 23),
        ("activate", 23, 30), ("choose", 30, 46), ("play", 46, 126),
        ("magnetize", 126, 196), ("move", 196, 245),
    )
    return next(label for label, start, stop in families if start <= action < stop)


def public_change(before: tuple[bytes, bytes, bytes],
                  after: tuple[bytes, bytes, bytes]) -> dict:
    """Compare first-party public feature, card and legality bytes only."""
    if any(not isinstance(v, bytes) for v in before + after):
        raise TypeError("Public snapshot components must be bytes")
    return {
        "features_changed": before[0] != after[0],
        "cards_changed": before[1] != after[1],
        "mask_changed": before[2] != after[2],
        "unchanged_public_observation": before == after,
    }


def probe(model_path: Path, expected_sha256: str, seed: int,
          max_actions: int = 220) -> dict:
    if not 1 <= max_actions <= 1000 or seed < 0:
        raise ValueError("Invalid finite public probe budget or seed")
    from .contract import ACTIONS, CARDS, FEATURES, verify_engine
    import numpy as np
    import taverngym
    from sb3_contrib import MaskablePPO

    engine = verify_engine()
    model_path = Path(model_path)
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if len(expected_sha256) != 64 or digest != expected_sha256:
        raise ValueError("Trusted model SHA256 mismatch")
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    if game.num_players != 8:
        raise RuntimeError("Expected exactly eight actual TavernGym seats")
    counts = Counter()
    state_counts = Counter()
    legal_buy_turns: set[int] = set()
    samples = []
    decisions = 0
    for _ in range(30000):
        if game.is_over() or decisions >= max_actions:
            break
        progressed = False
        for seat in range(game.num_players):
            if game.is_over() or decisions >= max_actions:
                break
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            turn = int(game.turn)
            f, c = game.observe2(0)
            raw_mask = game.legal_mask(0)
            features = np.frombuffer(f, dtype="<f4").copy()
            cards = np.frombuffer(c, dtype="<i4").copy()
            mask = np.frombuffer(raw_mask, dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned public observation dimensions changed")
            if not mask.any() or not np.isfinite(features).all():
                raise ValueError("Invalid public observation or legal action mask")
            action, _ = model.predict({"features": features, "cards": cards},
                                      action_masks=mask, deterministic=True)
            action = int(np.asarray(action).item())
            if not mask[action]:
                raise ValueError("Model selected an illegal action")
            family = action_family(action)
            has_legal_buy = bool(mask[8:16].any())
            if has_legal_buy:
                counts["legal_buy_decision_exposures"] += 1
                legal_buy_turns.add(turn)
            counts["family_" + family] += 1
            before = (f, c, raw_mask)
            game.step(0, action)
            decisions += 1
            result = None
            # Do not compare a new turn / other player's state to this action.
            if (not game.is_over() and int(game.turn) == turn
                    and game.needs_action(0)):
                next_f, next_c = game.observe2(0)
                next_mask = game.legal_mask(0)
                result = public_change(before, (next_f, next_c, next_mask))
                state_counts["comparable_same_turn_actions"] += 1
                if result["unchanged_public_observation"]:
                    state_counts["unchanged_public_actions"] += 1
                    state_counts["unchanged_family_" + family] += 1
                if result["cards_changed"]:
                    state_counts["cards_changed_family_" + family] += 1
            else:
                state_counts["poststate_not_comparable"] += 1
            if len(samples) < 60:
                samples.append({
                    "turn": turn, "action_id": action, "family": family,
                    "legal_buy": has_legal_buy, "poststate_comparable": result is not None,
                    "change": result,
                })
        if not progressed and not game.is_over():
            raise RuntimeError("Actual TavernGym game stopped advancing")
    completed = bool(game.is_over())
    result = {
        "schema": 1, "session_id": "s-20261103-71e4c9b2",
        "engine": engine, "model_sha256": digest, "seed": seed,
        "policy": "raw_ppo_no_guard_no_fallback",
        "completed": completed,
        "agent_rank": int(game.placements()[0]) if completed else None,
        "placements": [int(v) for v in game.placements()] if completed else None,
        "decisions": decisions, "max_actions": max_actions,
        "turns_with_legal_buy": len(legal_buy_turns),
        "action_counts": dict(counts), "public_changes": dict(state_counts),
        "first_60_actions": samples,
        "new_training_steps": 0, "champion_promoted": False,
        "limits": "Legal BUY does not prove optimal purchase; only comparable same-turn public snapshots are hashed. Incomplete probes are not complete-game receipts.",
    }
    if completed and sorted(result["placements"]) != list(range(1, 9)):
        raise RuntimeError("Final eight-player ranks are not a permutation")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--seed", type=int, default=99232)
    parser.add_argument("--max-actions", type=int, default=220)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = probe(args.model, args.sha256, args.seed, args.max_actions)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(json.dumps({
        "seed": args.seed, "complete": report["completed"], "rank": report["agent_rank"],
        "decisions": report["decisions"], "action_counts": report["action_counts"],
        "public_changes": report["public_changes"],
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
