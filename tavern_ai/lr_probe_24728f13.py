"""Isolated, real-engine MaskablePPO learning-rate ablation. Session s-20261102-24728f13.

Only artifacts from real TavernGym Game.is_over() simulations are written as receipts.
This is a guarded-model evaluation: forcing legal END_TURN after 40 actions
is recorded separately and is not claimed to be unconstrained model inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .env import TavernEnv
from .validate_receipt import validate

SESSION = "s-20261102-24728f13"
BASE_SHA = "315b068bac5ab6d8403c3c9b18f8c101c0cded5d"
TRAIN_SEED = 24728
EVAL_SEEDS = (42171, 42172, 42173)
ARM_LRS = {"reference": 3e-4, "candidate": 1e-4}
STEPS = 256
TURN_ACTION_BUDGET = 40


def choose_action(mask: np.ndarray, proposal: int | None, used: int, budget: int = TURN_ACTION_BUDGET) -> tuple[int, bool]:
    """Legal, auditable turn-cap override; never silently substitute an illegal action."""
    m = np.asarray(mask, dtype=bool)
    if m.shape != (ACTIONS,) or not m.any():
        raise ValueError("Invalid or empty TavernGym legal action mask")
    if used >= budget and m[0]:
        return 0, True
    if proposal is None or not 0 <= int(proposal) < ACTIONS or not m[int(proposal)]:
        raise ValueError(f"Model proposed illegal action: {proposal}")
    return int(proposal), False


def summary(receipts: list[dict]) -> dict:
    if not receipts:
        raise ValueError("No real match receipts")
    for receipt in receipts:
        validate(receipt)
        if sorted(receipt["placements"]) != list(range(1, 9)):
            raise ValueError("Placements are not a permutation of 1..8")
    ranks = [r["placements"][0] for r in receipts]
    return {
        "games": len(ranks),
        "ranks": ranks,
        "mean_rank": statistics.mean(ranks),
        "first_rate": sum(x == 1 for x in ranks) / len(ranks),
        "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
        "total_decisions": sum(r["decisions"] for r in receipts),
        "guard_forced_ends": sum(r["guard_forced_ends"] for r in receipts),
    }


def _save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def train_model(label: str, lr: float, out: Path, engine: dict):
    from sb3_contrib import MaskablePPO
    from .model import TavernExtractor
    env = TavernEnv(seed=TRAIN_SEED)
    try:
        model = MaskablePPO(
            "MultiInputPolicy", env, device="cpu", verbose=0, seed=TRAIN_SEED,
            n_steps=128, batch_size=64, n_epochs=4,
            gamma=0.99, gae_lambda=0.95, learning_rate=lr, ent_coef=0.01,
            policy_kwargs={
                "features_extractor_class": TavernExtractor,
                "features_extractor_kwargs": {"features_dim": 256},
                "net_arch": {"pi": [128], "vf": [128]},
            },
        )
        model.learn(total_timesteps=STEPS)
        executed = int(model.num_timesteps)
        if executed != STEPS:
            raise RuntimeError(f"Unexpected training steps: {executed}, expected {STEPS}")
        path = out / f"{label}.zip"
        path.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(path))
        if not path.exists():
            raise RuntimeError(f"Model checkpoint was not saved: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return model, {
            "label": label, "learning_rate": lr, "steps_executed": executed,
            "seed": TRAIN_SEED, "model_sha256": digest, "checkpoint_path": str(path),
            "engine": engine, "algorithm": "MaskablePPO",
            "policy": "MultiInputPolicy", "n_steps": 128, "batch_size": 64,
            "n_epochs": 4, "gamma": 0.99, "gae_lambda": 0.95,
            "ent_coef": 0.01, "turn_budget": TURN_ACTION_BUDGET,
        }
    finally:
        env.close()


def full_game(seed: int, label: str, model, model_sha: str, engine: dict) -> dict:
    import taverngym
    game = taverngym.Game(seed=seed)
    last_turn = -1
    used = 0
    decisions = 0
    guard_forced_ends = 0
    actual_model_actions = 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, used = turn, 0
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
                raise ValueError("Engine observation layout drift")
            if not np.isfinite(features).all():
                raise ValueError("Non-finite observation")
            if used >= TURN_ACTION_BUDGET and mask[0]:
                action, forced = choose_action(mask, None, used)
            else:
                predicted, _ = model.predict(
                    {"features": features, "cards": cards},
                    action_masks=mask, deterministic=True,
                )
                action, forced = choose_action(mask, int(np.asarray(predicted).item()), used)
                actual_model_actions += 1
            if forced:
                guard_forced_ends += 1
            if used >= 120:
                raise RuntimeError(f"Turn stuck: seed={seed}, turn={turn}, actions={used}")
            game.step(0, action)
            used += 1
            decisions += 1
        if not progressed and not game.is_over():
            raise RuntimeError(f"Game stalled at seed={seed}, turn={game.turn}")
    if not game.is_over():
        raise RuntimeError(f"Full-game safety limit exceeded: seed={seed}")
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION, "policy": "guarded_model",
        "arm": label, "seed": seed, "completed": bool(game.is_over()),
        "turns": int(game.turn), "decisions": decisions,
        "model_actions": actual_model_actions,
        "guard_forced_ends": guard_forced_ends,
        "turn_action_budget": TURN_ACTION_BUDGET,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "illegal_actions": 0, "git_sha": os.environ.get("GITHUB_SHA", ""),
        "model_sha256": model_sha,
    }
    validate(receipt)
    if sorted(receipt["placements"]) != list(range(1, 9)):
        raise ValueError("Non-permutation eight-seat result")
    return receipt


def run(out: Path, receipts_root: Path, reports_root: Path) -> dict:
    import torch
    torch.set_num_threads(2)
    engine = verify_engine()
    trainings = {}
    games = {}
    file_map = {}
    for arm, lr in ARM_LRS.items():
        model, info = train_model(arm, lr, out, engine)
        trainings[arm] = info
        games[arm], file_map[arm] = [], []
        for seed in EVAL_SEEDS:
            receipt = full_game(seed, arm, model, info["model_sha256"], engine)
            path = receipts_root / (f"001-{seed}.json" if arm == "candidate" else f"001-reference-{seed}.json")
            _save_json(path, receipt)
            file_map[arm].append(str(path))
            games[arm].append(receipt)
            print(f"{arm} seed={seed}: rank={receipt['placements'][0]} "
                  f"decisions={receipt['decisions']} guarded_ends={receipt['guard_forced_ends']}", flush=True)
    for arm in ARM_LRS:
        _save_json(out / f"{arm}.metadata.json", trainings[arm])
    analysis = {
        "session_id": SESSION, "round": 1,
        "base_main_sha": BASE_SHA,
        "run_sha": os.environ.get("GITHUB_SHA", ""),
        "engine": engine,
        "research_hypothesis": "Smaller PPO learning rate might improve short-run placement and guard stability",
        "independent_eval_seeds": list(EVAL_SEEDS),
        "training": trainings, "receipts": file_map,
        "summary": {arm: summary(games[arm]) for arm in ARM_LRS},
        "paired_candidate_minus_reference_rank": [
            c["placements"][0] - b["placements"][0]
            for c, b in zip(games["candidate"], games["reference"])
        ],
        "interpretation": "Exploratory pilot; three heldout matches per arm are insufficient to establish strength.",
        "model_state": "CANDIDATE only; no Best promotion; temporary Actions Artifact (30 days).",
    }
    analysis["paired_mean_rank_delta"] = statistics.mean(analysis["paired_candidate_minus_reference_rank"])
    _save_json(reports_root / "001-lr-ablation.json", analysis)
    print(json.dumps({"summary": analysis["summary"], "paired_mean_rank_delta": analysis["paired_mean_rank_delta"]},
                     ensure_ascii=False), flush=True)
    return analysis


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=Path("outputs") / SESSION)
    parser.add_argument("--receipts-dir", type=Path, default=Path("experiments") / SESSION)
    parser.add_argument("--reports-dir", type=Path, default=Path("reports") / SESSION)
    args = parser.parse_args()
    run(args.model_dir, args.receipts_dir, args.reports_dir)


if __name__ == "__main__":
    main()
