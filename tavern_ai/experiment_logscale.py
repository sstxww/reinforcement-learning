"""Paired, bounded, real-engine MaskablePPO numeric-encoding experiment.

This module owns only its session files; it never modifies shared training code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch as th

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .env import TavernEnv
from .log_extractor import LogTavernExtractor
from .model import TavernExtractor
from .validate_receipt import validate


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def train_variant(kind: str, extractor, steps: int, seed: int, directory: Path, engine: dict) -> dict:
    from sb3_contrib import MaskablePPO

    directory.mkdir(parents=True, exist_ok=True)
    env = TavernEnv(seed=seed)
    checkpoint = directory / (kind + ".zip")
    started = time.perf_counter()
    try:
        observation, _ = env.reset(seed=seed)
        mask = env.action_masks()
        if (observation["features"].shape != (FEATURES,)
                or observation["cards"].shape != (CARDS,)
                or mask.shape != (ACTIONS,) or not mask.any()):
            raise RuntimeError("Pinned observation or action mask failed contract preflight")
        action = int(np.flatnonzero(mask)[0])
        env.step(action)  # Test actual legal-action execution before PPO training.
        model = MaskablePPO(
            "MultiInputPolicy", env, device="cpu", verbose=1, seed=seed,
            n_steps=128, batch_size=64, n_epochs=2, gamma=0.99,
            gae_lambda=0.95, learning_rate=3e-4, ent_coef=0.01,
            policy_kwargs={
                "features_extractor_class": extractor,
                "features_extractor_kwargs": {"features_dim": 256},
                "net_arch": {"pi": [128], "vf": [128]},
            },
        )
        model.learn(total_timesteps=steps, reset_num_timesteps=True)
        model.save(str(checkpoint))
        metadata = {
            "schema": 1, "engine": engine, "training_seed": seed,
            "algorithm": "MaskablePPO", "timesteps": int(model.num_timesteps),
            "numeric_preprocess": kind,
            "ppo": {"n_steps": 128, "batch_size": 64, "n_epochs": 2,
                    "gamma": 0.99, "gae_lambda": 0.95, "learning_rate": 0.0003,
                    "ent_coef": 0.01},
            "sha256": sha256(checkpoint),
        }
        (directory / (kind + ".metadata.json")).write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
        return {
            "checkpoint": str(checkpoint),
            "checkpoint_sha256": metadata["sha256"],
            "metadata": str(directory / (kind + ".metadata.json")),
            "actual_timesteps": int(model.num_timesteps),
            "train_seconds": round(time.perf_counter() - started, 2),
        }
    finally:
        env.close()



def bounded_full_game(seed: int, agent_id: str, model_path: str) -> dict:
    """Full eight-seat engine match using deterministic PPO with one uniform turn cap.

    The cap is part of BOTH experimental policies, not an artificial game result.
    Unbounded 256-step random-init PPO reached the global 30k loop guard in run
    41412975503. For fairness, both arms end a turn at 45 decisions whenever
    END_TURN (action 0) is legal.
    """
    import taverngym
    from sb3_contrib import MaskablePPO

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    model = MaskablePPO.load(model_path, device="cpu")
    decisions = 0
    forced_end_turns = 0
    actions_this_turn = 0
    last_turn = -1
    for _ in range(30000):
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
                raise ValueError("Unexpected observe2 or legal-mask contract")
            if not np.isfinite(f).all() or not mask.any():
                raise ValueError("Non-finite features or empty action mask")
            if actions_this_turn >= 45 and mask[0]:
                action = 0
                forced_end_turns += 1
            else:
                action, _ = model.predict(
                    {"features": f, "cards": c},
                    action_masks=mask, deterministic=True
                )
                action = int(action)
            if not mask[action]:
                raise RuntimeError("Model proposed an illegal TavernGym action")
            game.step(0, action)
            actions_this_turn += 1
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled without action")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded even with turn cap")
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": "model",
        "policy_action_cap": 45,
        "forced_end_turns": forced_end_turns,
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "model_sha256": sha256(Path(model_path)),
    }
    validate(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--steps", type=int, default=256)
    parser.add_argument("--train-seed", type=int, default=71002)
    parser.add_argument("--eval-seed-start", type=int, default=32001)
    parser.add_argument("--games", type=int, default=3)
    args = parser.parse_args()
    if (not args.session_id.startswith("s-") or "/" in args.session_id
            or "\\" in args.session_id):
        raise ValueError("Invalid independent session ID")
    if args.steps < 128 or args.steps % 128:
        raise ValueError("PPO steps must be a positive multiple of 128")
    if not 1 <= args.games <= 5:
        raise ValueError("Evaluation games must be 1..5")

    th.set_num_threads(2)
    engine = verify_engine()
    receipts = Path("experiments") / args.session_id
    checkpoints = Path("checkpoints") / args.session_id
    receipts.mkdir(parents=True, exist_ok=True)
    results = {
        "schema": 1,
        "session_id": args.session_id,
        "hypothesis": "signed-log compression stabilizes numeric input scaling",
        "engine": engine,
        "training_seed": args.train_seed,
        "eval_seeds": list(range(args.eval_seed_start, args.eval_seed_start + args.games)),
        "requested_steps_per_variant": args.steps,
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_sha": os.environ.get("GITHUB_SHA"),
        "variants": {},
    }
    for variant, extractor in (
        ("raw", TavernExtractor),
        ("signed_log1p", LogTavernExtractor),
    ):
        train_data = train_variant(
            variant, extractor, args.steps, args.train_seed, checkpoints, engine
        )
        games = []
        for index, seed in enumerate(results["eval_seeds"]):
            receipt = (receipts / (f"001-{seed}.json" if variant == "signed_log1p" and index == 0
                                  else f"{variant}-{seed}.json"))
            match = bounded_full_game(seed, args.session_id, train_data["checkpoint"])
            validate(match)
            receipt.write_text(json.dumps(match, indent=2) + "\n", encoding="utf-8")
            games.append({
                "seed": seed, "placement": match["placements"][0],
                "all_placements": match["placements"],
                "decisions": match["decisions"],
                "turns": match["turns"],
                "truncated_combats": match["truncated_combats"],
                "turn_limit_end": match["turn_limit_end"],
                "receipt": str(receipt),
            })
            print(json.dumps({"variant": variant, "seed": seed,
                              "placement": match["placements"][0], "completed": True}),
                  flush=True)
        places = [x["placement"] for x in games]
        results["variants"][variant] = {
            "training": train_data, "matches": games,
            "mean_placement": statistics.mean(places),
            "top4_rate": sum(p <= 4 for p in places) / len(places),
            "first_rate": sum(p == 1 for p in places) / len(places),
        }

    raw_places = [x["placement"] for x in results["variants"]["raw"]["matches"]]
    log_places = [x["placement"] for x in results["variants"]["signed_log1p"]["matches"]]
    results["paired_placement_delta_log_minus_raw"] = [
        log - raw for log, raw in zip(log_places, raw_places)
    ]
    results["total_real_ppo_steps"] = sum(
        data["training"]["actual_timesteps"] for data in results["variants"].values()
    )
    results["interpretation"] = (
        "Paired pilot only; three seeds cannot establish a statistically reliable strength gain."
    )
    (receipts / "comparison.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
