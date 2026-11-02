"""Read-only action-probability probe for the V5 rank-eight, zero-BUY symptom.

Uses ONLY legal public observe2 observations and the already trained MaskablePPO.
It never modifies policy actions, trains, forces END, or asserts that BUY is optimal.
The returned full-match status is diagnostic; an official canary receipt is separate.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np

from .contract import ACTIONS, CARDS, FEATURES, verify_engine

FAMILIES = (
    ("end_turn", 0, 1), ("refresh", 1, 2), ("freeze", 2, 3),
    ("upgrade", 3, 4), ("hero_power", 4, 6), ("dark_gift", 6, 7),
    ("cancel", 7, 8), ("buy", 8, 16), ("sell", 16, 23),
    ("activate", 23, 30), ("choose", 30, 46), ("play", 46, 126),
    ("magnetize", 126, 196), ("move", 196, 245),
)


def family(action: int) -> str:
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError("Invalid action ID")
    return next(name for name, first, last in FAMILIES if first <= action < last)


def summarize_probabilities(probs, mask, action: int) -> dict:
    """Validate the actual masked action probabilities and return public diagnostics.

    The policy exposes a probability distribution over all 245 action IDs. Legal
    BUY exposures are repeated decision states, NOT independent purchase offers.
    """
    p = np.asarray(probs, dtype=np.float64)
    legal = np.asarray(mask, dtype=bool)
    if p.shape != (ACTIONS,) or legal.shape != (ACTIONS,) or not legal.any():
        raise ValueError("Invalid masked policy distribution shape")
    if not np.isfinite(p).all() or (p < -1e-8).any():
        raise ValueError("Non-finite or negative masked probability")
    if not np.isclose(p.sum(), 1.0, atol=1e-4):
        raise ValueError("Masked action probability is not normalized")
    if np.any(p[~legal] > 1e-5):
        raise ValueError("Illegal action received positive probability")
    if type(action) is not int or not 0 <= action < ACTIONS or not legal[action]:
        raise ValueError("Model selected illegal action")
    buy_legal = bool(legal[8:16].any())
    active = p[p > 0]
    return {
        "buy_legal": buy_legal,
        "legal_buy_slots": int(legal[8:16].sum()),
        "legal_action_count": int(legal.sum()),
        "buy_probability": float(p[8:16].sum()),
        "best_buy_probability": float(p[8:16].max()) if buy_legal else 0.0,
        "refresh_freeze_probability": float(p[1:3].sum()),
        "end_turn_probability": float(p[0]),
        "play_probability": float(p[46:126].sum()),
        "selected_action_probability": float(p[action]),
        "top_action_probability": float(p.max()),
        "masked_entropy_nats": float(-(active * np.log(active)).sum()),
    }


def run_probe(model_path: Path, expected_sha256: str, seed: int,
              max_decisions: int = 1200) -> dict:
    if seed < 0 or not 1 <= max_decisions <= 5000:
        raise ValueError("Invalid seed or decision budget")
    if len(expected_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_sha256):
        raise ValueError("Require exact lowercase expected SHA256")
    digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if digest != expected_sha256:
        raise ValueError("Model bytes do not match pinned Release SHA256")

    import taverngym
    import torch
    from sb3_contrib import MaskablePPO

    engine = verify_engine()
    torch.set_num_threads(2)
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    if game.num_players != 8:
        raise ValueError("Expected an eight-seat real TavernGym game")

    counts = Counter()
    per_turn = defaultdict(Counter)
    legal_buy_stats = Counter()
    examples = []
    decisions = 0
    budget_exhausted = False

    for _ in range(30000):
        if game.is_over():
            break
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            if decisions >= max_decisions:
                budget_exhausted = True
                break
            fbytes, cbytes = game.observe2(0)
            f = np.frombuffer(fbytes, dtype="<f4").copy()
            c = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,) or not mask.any():
                raise ValueError("Public observation/action mask contract mismatch")
            obs = {"features": f, "cards": c}
            with torch.no_grad():
                tensor_obs, _ = model.policy.obs_to_tensor(obs)
                dist = model.policy.get_distribution(
                    tensor_obs, action_masks=mask.reshape(1, -1))
                probs = dist.distribution.probs.detach().cpu().numpy().reshape(-1)
            selected, _ = model.predict(obs, action_masks=mask, deterministic=True)
            action = int(np.asarray(selected).item())
            snap = summarize_probabilities(probs, mask, action)
            kind = family(action)
            counts[kind] += 1
            turn = str(int(game.turn))
            per_turn[turn]["decisions"] += 1
            per_turn[turn][kind] += 1
            if snap["buy_legal"]:
                per_turn[turn]["buy_legal_exposures"] += 1
                legal_buy_stats["exposures"] += 1
                legal_buy_stats["selected_buy"] += int(kind == "buy")
                for key in (
                    "buy_probability", "best_buy_probability",
                    "refresh_freeze_probability", "end_turn_probability",
                    "play_probability", "selected_action_probability",
                    "top_action_probability", "masked_entropy_nats",
                    "legal_buy_slots", "legal_action_count",
                ):
                    legal_buy_stats[key] += snap[key]
                if len(examples) < 12:
                    examples.append({
                        "turn": int(game.turn),
                        "chosen_family": kind,
                        "legal_buy_slots": snap["legal_buy_slots"],
                        "buy_probability": round(snap["buy_probability"], 5),
                        "refresh_freeze_probability": round(snap["refresh_freeze_probability"], 5),
                        "top_action_probability": round(snap["top_action_probability"], 5),
                    })
            game.step(0, action)
            decisions += 1
        if budget_exhausted:
            break
        if not progressed and not game.is_over():
            raise RuntimeError("Real game stalled without an actionable seat")
    completed = bool(game.is_over())
    if completed and sorted(int(x) for x in game.placements()) != list(range(1, 9)):
        raise ValueError("Completed game placements are not a permutation of 1..8")

    n = int(legal_buy_stats["exposures"])
    averaged = {
        "decision_state_exposures": n,
        "selected_buy_count": int(legal_buy_stats["selected_buy"]),
    }
    for key in (
        "buy_probability", "best_buy_probability",
        "refresh_freeze_probability", "end_turn_probability",
        "play_probability", "selected_action_probability",
        "top_action_probability", "masked_entropy_nats",
        "legal_buy_slots", "legal_action_count",
    ):
        averaged["mean_" + key] = (
            round(legal_buy_stats[key] / n, 6) if n else None
        )

    return {
        "schema": 1,
        "session_id": "s-20261103-630ed53f",
        "policy": "raw_model_no_fallback",
        "model_sha256": digest,
        "seed": seed,
        "engine": engine,
        "completed": completed,
        "incomplete_reason": None if completed else "bounded_decision_budget_or_simulator_loop",
        "turns_reached": int(game.turn),
        "model_rank": int(game.placements()[0]) if completed else None,
        "model_decisions": decisions,
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "action_counts": dict(sorted(counts.items())),
        "per_turn": {k: dict(v) for k, v in sorted(per_turn.items(), key=lambda t: int(t[0]))},
        "when_buy_is_mask_legal": averaged,
        "example_public_decisions": examples,
        "forced_end_turns": 0,
        "baseline_fallback_actions": 0,
        "ppo_training_steps_this_probe": 0,
        "promoted_to_champion": False,
        "not_an_official_canary_receipt": True,
        "limitations": [
            "Each legal-BUY exposure is a possibly correlated decision state, not an independent good buying opportunity.",
            "Probability concentration in REFRESH/FREEZE is an observed policy outcome; this probe alone cannot identify the reward, features, or optimizer as a cause.",
            "Only raw model actions are used. If the game is incomplete, do not treat it as a completed match.",
            "Rank is not a strength difference without comparable independently seeded baseline/model evaluation.",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--max-decisions", type=int, default=1200)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = run_probe(args.model, args.expected_sha256, args.seed, args.max_decisions)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "completed": result["completed"],
        "model_rank": result["model_rank"],
        "actions": result["action_counts"],
        "when_buy_legal": result["when_buy_is_mask_legal"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
