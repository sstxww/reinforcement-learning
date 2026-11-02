"""Isolated real TavernGym purchase-slot ablation: no simulator mocks."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import random
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from tavern_ai.baseline import BaselinePolicy
from tavern_ai.contract import ACTIONS, CARDS, FEATURES, verify_engine
from tavern_ai.validate_receipt import validate

SESSION_ID = "s-20261102-1d9e7456"
MODES = ("baseline", "uniform", "rightmost")
TRAIN_SEEDS = (38100, 38101)
EVAL_SEEDS = (38200, 38201, 38202)
MAX_GAME_SECONDS = 900

class PurchasePolicy:
    """Only alter tie-breaking of the original baseline purchase action."""
    def __init__(self, mode: str, seed: int):
        if mode not in MODES:
            raise ValueError(f"Unknown mode: {mode}")
        self.mode, self.base = mode, BaselinePolicy()
        self.rng = random.Random(seed * 431 + 11)
        self.choice_opportunities = 0
        self.changed_from_first = 0

    def act(self, observation: dict, context: dict | None = None) -> int:
        original = int(self.base.act(observation, context))
        if self.mode == "baseline" or not 8 <= original < 16:
            return original
        mask = np.asarray(observation["action_mask"], dtype=bool)
        buys = (np.flatnonzero(mask[8:16]) + 8).tolist()
        if len(buys) < 2:
            return original
        self.choice_opportunities += 1
        alternative = self.rng.choice(buys) if self.mode == "uniform" else buys[-1]
        self.changed_from_first += int(alternative != original)
        return int(alternative)

def play(seed: int, mode: str, engine: dict) -> dict:
    import taverngym
    game = taverngym.Game(seed=seed)
    policy = PurchasePolicy(mode, seed)
    decisions, last_turn, actions_this_turn = 0, -1, 0
    start = time.monotonic()
    for _ in range(30000):
        if time.monotonic() - start > MAX_GAME_SECONDS:
            raise TimeoutError(f"Real-game budget exceeded: {mode=} {seed=}")
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, actions_this_turn = turn, 0
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(0)
            f = np.frombuffer(fbytes, dtype="<f4").copy()
            c = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Unexpected observe2 contract")
            if not mask.any():
                raise ValueError("Empty legal mask")
            action = policy.act(
                {"features": f, "cards": c, "action_mask": mask},
                {"turn": turn, "actions_used": actions_this_turn})
            if not mask[action]:
                raise ValueError(f"Illegal experimental action: {action}")
            game.step(0, int(action))
            decisions += 1
            actions_this_turn += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Game iteration safety limit exceeded")
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"], "agent_id": SESSION_ID,
        "policy": "purchase-slot-" + mode, "seed": seed, "completed": True,
        "turns": int(game.turn), "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""), "model_sha256": None,
        "buy_choice_opportunities": policy.choice_opportunities,
        "buy_choices_changed": policy.changed_from_first,
        "illegal_actions": 0, "runtime_seconds": round(time.monotonic() - start, 3),
    }
    validate(receipt)
    if sorted(receipt["placements"]) != list(range(1, 9)):
        raise AssertionError("Invalid eight-seat placement permutation")
    print(json.dumps({"seed": seed, "mode": mode, "rank": receipt["placements"][0],
        "decisions": decisions, "completed": True,
        "buy_choice_opportunities": policy.choice_opportunities,
        "runtime_seconds": receipt["runtime_seconds"]}), flush=True)
    return receipt

def metrics(records: list[dict]) -> dict:
    places = [r["placements"][0] for r in records]
    return {
        "games": len(places), "mean_placement": statistics.mean(places),
        "top4_rate": sum(p <= 4 for p in places) / len(places),
        "first_place_rate": sum(p == 1 for p in places) / len(places),
        "seat_zero_placements": places,
        "total_decisions": sum(r["decisions"] for r in records),
        "buy_choice_opportunities": sum(r["buy_choice_opportunities"] for r in records),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("research/sessions") / SESSION_ID)
    p.add_argument("--receipt", type=Path,
                   default=Path("experiments") / SESSION_ID / "001-38200.json")
    args = p.parse_args()
    engine = verify_engine()
    if (engine["features"], engine["cards"], engine["actions"]) != (4017, 447, 245):
        raise ValueError("Unrecognized engine contract")
    training = {m: [play(s, m, engine) for s in TRAIN_SEEDS] for m in MODES}
    calibration = {m: metrics(rows) for m, rows in training.items()}
    selected = min(MODES, key=lambda m: (calibration[m]["mean_placement"], MODES.index(m)))
    holdout = {"baseline": [play(s, "baseline", engine) for s in EVAL_SEEDS]}
    if selected != "baseline":
        holdout[selected] = [play(s, selected, engine) for s in EVAL_SEEDS]
    holdout_metrics = {m: metrics(rows) for m, rows in holdout.items()}
    args.out.mkdir(parents=True, exist_ok=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(holdout[selected][0], indent=2) + "\n", encoding="utf-8")
    selection = {
        "schema": 1, "session_id": SESSION_ID,
        "algorithm": "real-game purchase-slot rule calibration (NOT PPO)",
        "selected_mode": selected, "train_seeds": list(TRAIN_SEEDS),
        "holdout_seeds": list(EVAL_SEEDS), "calibration_metrics": calibration,
        "training_games": sum(len(v) for v in training.values()),
        "training_agent_decisions": sum(r["decisions"] for rows in training.values() for r in rows),
        "training_ppo_steps": 0, "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "source_commit": os.getenv("GITHUB_SHA", ""),
    }
    model_bytes = (json.dumps(selection, sort_keys=True, indent=2) + "\n").encode()
    (args.out / "selected-policy.json").write_bytes(model_bytes)
    report = {
        "schema": 1, "session_id": SESSION_ID,
        "hypothesis": "Seeded uniform purchase slot breaks first-slot bias",
        "base_sha": "6ac59235b8238196a0e6462de77b72413c829372",
        "engine": engine,
        "selection_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "selection": selection, "heldout_metrics": holdout_metrics,
        "all_training_receipts": training, "all_holdout_receipts": holdout,
        "delta_mean_placement_vs_baseline": (
            holdout_metrics[selected]["mean_placement"] - holdout_metrics["baseline"]["mean_placement"]
        ),
        "evidence_limits": "2 calibration seeds/mode, 3 heldout seeds; cannot establish improvement.",
    }
    (args.out / "metrics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected": selected, "calibration": calibration,
        "heldout": holdout_metrics, "selection_sha256": report["selection_sha256"]}), flush=True)

if __name__ == "__main__":
    main()
