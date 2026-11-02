"""Small bounded public-observation intervention to isolate two model pathologies.

This is deliberately a HYBRID research policy, not a stronger pure PPO.
Never supply non-public engine state to the model; never force an illegal move.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import statistics

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SEEDS = (83701, 83702, 83801, 83802)
SESSION = "s-20261102-9732a21e"
MAX_ACTIONS_PER_TURN = 35
MAX_FORCE_BUYS_PER_TURN = 2


def intervention(proposed: int, mask: np.ndarray, actions_this_turn: int,
                 forced_buys_this_turn: int) -> tuple[int, str]:
    """One-factor diagnostic: restore economy and avoid thousands of optional moves."""
    if mask.shape != (ACTIONS,) or mask.dtype != bool or not mask.any():
        raise ValueError("Legal action mask mismatch")
    if not isinstance(proposed, int) or not 0 <= proposed < ACTIONS or not mask[proposed]:
        raise ValueError("Policy proposed an illegal action")
    # Never ignore an in-progress mandatory choice; no change to forced-choice semantics.
    choices = np.flatnonzero(mask[30:46])
    if len(choices):
        return proposed, "none"
    if actions_this_turn >= MAX_ACTIONS_PER_TURN and mask[0]:
        return 0, ("turn_budget" if proposed != 0 else "none")
    buys = np.flatnonzero(mask[8:16])
    if len(buys) and forced_buys_this_turn < MAX_FORCE_BUYS_PER_TURN:
        if not 8 <= proposed < 16:
            return int(buys[0] + 8), "buy_priority"
    return proposed, "none"


def one_game(seed: int, label: str, model, model_sha: str, engine: dict):
    import taverngym
    game = taverngym.Game(seed=seed)
    baseline = BaselinePolicy()
    turn = -1
    used = 0
    forced_buys_this_turn = 0
    decisions = 0
    guard_counts = Counter()
    actions = Counter()
    legal_buy_opportunities = 0
    buy_actions = 0
    for _ in range(30000):
        if game.is_over():
            break
        t = int(game.turn)
        if t != turn:
            turn, used, forced_buys_this_turn = t, 0, 0
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
                raise ValueError("Unexpected pinned observe2 sizes")
            if not np.isfinite(features).all():
                raise ValueError("Nonfinite public features")
            if bool(mask[8:16].any()):
                legal_buy_opportunities += 1
            if label == "guarded_model":
                proposed, _ = model.predict({"features": features, "cards": cards},
                                            action_masks=mask, deterministic=True)
                action, intervention_kind = intervention(int(np.asarray(proposed).item()),
                                                         mask, used, forced_buys_this_turn)
                if intervention_kind == "buy_priority":
                    forced_buys_this_turn += 1
            elif label == "baseline":
                action = int(baseline.act({"features": features, "cards": cards,
                                           "action_mask": mask},
                                          {"turn": t, "actions_used": used}))
                intervention_kind = "none"
            else:
                raise ValueError("Unknown policy")
            if not mask[action]:
                raise ValueError("Illegal selected action")
            game.step(0, action)
            decisions += 1
            used += 1
            guard_counts[intervention_kind] += 1
            actions["buy" if 8 <= action < 16 else
                    "end_turn" if action == 0 else
                    "play" if 46 <= action < 126 else
                    "cancel" if action == 7 else "other"] += 1
            if 8 <= action < 16:
                buy_actions += 1
        if not progressed and not game.is_over():
            break
    completed = bool(game.is_over()) and not int(game.truncated_combats) and not bool(game.turn_limit_end)
    diagnostic = {
        "seed": seed, "policy_variant": label, "completed": completed,
        "failure": None if completed else "incomplete_or_engine_guarded",
        "decisions": decisions, "turns_reached": int(game.turn),
        "model_sha256": model_sha if label == "guarded_model" else None,
        "legal_buy_opportunities": legal_buy_opportunities,
        "buy_actions": buy_actions,
        "rule_overrides": {key: value for key, value in guard_counts.items() if key != "none"},
        "action_categories": dict(actions),
        "hybrid_policy": label == "guarded_model",
        "model_training_steps_this_study": 0,
    }
    if not completed:
        return diagnostic, None
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"], "agent_id": SESSION,
        "policy": "guarded_model_diagnostic" if label == "guarded_model" else "baseline",
        "seed": seed, "completed": True, "turns": int(game.turn), "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "model_sha256": model_sha if label == "guarded_model" else None,
        "rule_interventions": diagnostic["rule_overrides"],
        "git_sha": os.getenv("GITHUB_SHA", ""),
    }
    validate(receipt)
    if sorted(receipt["placements"]) != list(range(1, 9)):
        raise ValueError("Not a complete eight-seat placement permutation")
    diagnostic["rank"] = receipt["placements"][0]
    return diagnostic, receipt


def main():
    from sb3_contrib import MaskablePPO
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--receipt-dir", type=Path, required=True)
    a = p.parse_args()
    engine = verify_engine()
    model_sha = hashlib.sha256(a.model.read_bytes()).hexdigest()
    model = MaskablePPO.load(str(a.model), device="cpu")
    a.receipt_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for seed in SEEDS:
        for label in ("guarded_model", "baseline"):
            result, receipt = one_game(seed, label, model, model_sha, engine)
            results.append(result)
            if receipt is not None:
                (a.receipt_dir / f"003-{seed}-{label}.json").write_text(
                    json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(result), flush=True)
    pairs = []
    for seed in SEEDS:
        g = next(v for v in results if v["seed"] == seed and v["policy_variant"] == "guarded_model")
        b = next(v for v in results if v["seed"] == seed and v["policy_variant"] == "baseline")
        if g["completed"] and b["completed"]:
            pairs.append({"seed": seed, "hybrid_rank": g["rank"],
                          "baseline_rank": b["rank"], "delta": g["rank"] - b["rank"]})
    out = {
        "schema": 1, "session_id": SESSION, "study": "HYBRID_RULE_OVERRIDE_ABLATION",
        "training_steps": 0, "source_unpromoted_release":
            "v5-resume-smoke-s-20261102-9732a21e-r001",
        "source_model_sha256": model_sha,
        "model_is_champion": False, "seeds": list(SEEDS),
        "results": results, "paired_completed_count": len(pairs), "pairs": pairs,
        "mean_paired_rank_delta_if_comparable":
            statistics.mean(p["delta"] for p in pairs) if pairs else None,
        "interpretation": "Proof of policy-behavior effect only; rule-overridden hybrid is NOT pure PPO; n=4 exploratory.",
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"paired_count": len(pairs), "model_weight_sha256": model_sha}), flush=True)


if __name__ == "__main__":
    main()
