"""Isolated V7 seat-rotation probe: genuine TavernGym eight-player games.

Never substitute baseline on model failure. Raw action IDs are *not* decoded into
families without a separately verified pinned-engine mapping. Diagnostic failure
JSON is not a completed-game receipt or a ranking.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from tavern_ai.baseline import BaselinePolicy
from tavern_ai.contract import ACTIONS, CARDS, FEATURES, verify_engine
from tavern_ai.receipt_integrity import validate_integrity


def validate_settings(seed: int, seat: int, policy: str, max_actions: int) -> None:
    if type(seed) is not int or seed < 0:
        raise ValueError("Seed must be a nonnegative integer")
    if type(seat) is not int or seat not in range(1, 8):
        raise ValueError("This probe requires a non-zero controlled seat 1..7")
    if policy not in ("baseline", "model"):
        raise ValueError("Policy must be baseline or model")
    if type(max_actions) is not int or not 1 <= max_actions <= 6000:
        raise ValueError("Max controlled decisions must be 1..6000")


def complete_receipt(*, engine: dict, game, seed: int, seat: int,
                     policy: str, decisions: int, model_sha: str | None,
                     diagnostics: dict) -> dict:
    places = [int(x) for x in game.placements()]
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": "s-20261103-6d43ab93",
        "seed": seed, "seat": seat, "policy": policy,
        "completed": True, "turns": int(game.turn),
        "decisions": decisions,
        "placements": places, "agent_placement": places[seat],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "model_sha256": model_sha,
        "guard_forced_ends": 0, "fallback_actions": 0,
        "raw_action_diagnostics": diagnostics,
    }
    validate_integrity(receipt)
    if receipt["agent_placement"] != receipt["placements"][seat]:
        raise AssertionError("Wrong controlled-seat rank")
    return receipt


def run(seed: int, seat: int, policy: str, model_path: Path | None,
        max_actions: int = 6000) -> tuple[dict, bool]:
    validate_settings(seed, seat, policy, max_actions)
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    if game.num_players != 8:
        raise RuntimeError("Expected exactly eight TavernGym players")
    baseline = BaselinePolicy()
    model = None
    model_sha = None
    if policy == "model":
        if model_path is None or not model_path.is_file():
            raise FileNotFoundError("Raw PPO checkpoint missing")
        from sb3_contrib import MaskablePPO
        model_sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
        model = MaskablePPO.load(str(model_path), device="cpu")
    decisions, last_turn, actions_this_turn = 0, None, 0
    hist: Counter[int] = Counter()
    recent = deque(maxlen=64)
    consecutive_same_observation = 0
    prior_digest = None

    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, actions_this_turn, prior_digest = turn, 0, None
        advanced = False
        for player in range(game.num_players):
            if not game.needs_action(player):
                continue
            advanced = True
            if player != seat:
                game.bot_play(player)
                continue
            if decisions >= max_actions:
                report = {
                    "schema": 1, "environment": "TavernGym",
                    "completed": False, "failure": "controlled_action_budget_exhausted",
                    "seed": seed, "seat": seat, "policy": policy,
                    "model_sha256": model_sha, "turn": int(game.turn),
                    "raw_decisions": decisions, "max_actions": max_actions,
                    "guard_forced_ends": 0, "fallback_actions": 0,
                    "same_observation_consecutive": consecutive_same_observation,
                    "raw_action_histogram": dict(sorted(hist.items())),
                    "recent_public_observation_and_raw_actions": list(recent),
                    "note": "Failure diagnostic only; never assign eighth place.",
                }
                return report, False
            float_bytes, card_bytes = game.observe2(seat)
            features = np.frombuffer(float_bytes, dtype="<f4").copy()
            cards = np.frombuffer(card_bytes, dtype="<i4").copy()
            legal = np.frombuffer(game.legal_mask(seat), dtype=np.uint8).astype(bool)
            if (features.shape, cards.shape, legal.shape) != (
                    (FEATURES,), (CARDS,), (ACTIONS,)):
                raise RuntimeError("Pinned observe2/mask shape changed")
            if not legal.any():
                raise RuntimeError("Controlled seat has zero legal actions")
            digest = hashlib.blake2b(
                float_bytes + card_bytes + legal.astype("u1").tobytes(),
                digest_size=12).hexdigest()
            if digest == prior_digest:
                consecutive_same_observation += 1
            prior_digest = digest
            if model is None:
                action = baseline.act(
                    {"features": features, "cards": cards, "action_mask": legal},
                    {"turn": turn, "actions_used": actions_this_turn})
            else:
                action, _ = model.predict(
                    {"features": features, "cards": cards},
                    action_masks=legal, deterministic=True)
            action = int(action)
            if not 0 <= action < ACTIONS or not legal[action]:
                raise RuntimeError("Policy proposed illegal raw action")
            recent.append({"turn": turn, "raw_action": action,
                           "visible_obs_digest": digest, "legal_count": int(legal.sum())})
            hist[action] += 1
            game.step(seat, action)
            decisions += 1
            actions_this_turn += 1
        if not advanced and not game.is_over():
            raise RuntimeError("Game stalled without legal actor")
    if not game.is_over():
        return {
            "schema": 1, "completed": False, "failure": "global_game_iteration_cap",
            "seed": seed, "seat": seat, "policy": policy,
            "model_sha256": model_sha, "raw_decisions": decisions,
            "recent_public_observation_and_raw_actions": list(recent),
            "note": "Incomplete, no placement.",
        }, False

    diag = {
        "raw_action_histogram": dict(sorted(hist.items())),
        "same_observation_consecutive": consecutive_same_observation,
        "recent_public_observation_and_raw_actions": list(recent),
        "raw_model_no_fallback": policy == "model",
    }
    return complete_receipt(
        engine=engine, game=game, seed=seed, seat=seat,
        policy=policy, decisions=decisions, model_sha=model_sha,
        diagnostics=diag), True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=99741)
    parser.add_argument("--seat", type=int, default=1)
    parser.add_argument("--policy", choices=("baseline", "model"), required=True)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--max-actions", type=int, default=6000)
    parser.add_argument("--out", type=Path, required=True)
    a = parser.parse_args()
    receipt, completed = run(a.seed, a.seat, a.policy, a.model, a.max_actions)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    print(json.dumps({
        "completed": completed, "seed": a.seed, "seat": a.seat,
        "policy": a.policy,
        "placement": receipt.get("agent_placement") if completed else None,
        "decision_count": receipt.get("decisions", receipt.get("raw_decisions")),
        "reason": receipt.get("failure"), "model_sha256": receipt.get("model_sha256"),
    }, ensure_ascii=False))
    if not completed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
