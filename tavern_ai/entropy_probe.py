"""Session-isolated real TavernGym PPO entropy-coefficient experiment."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

from .contract import verify_engine
from .validate_receipt import validate

VARIANTS = {"zero": 0.0, "regularized": 0.02}


def aggregate(records):
    if not records:
        raise ValueError("No match records")
    for result in records:
        validate(result)
    ranks = [r["placements"][0] for r in records]
    return {
        "games": len(ranks),
        "seeds": [r["seed"] for r in records],
        "placements": ranks,
        "mean_placement": statistics.mean(ranks),
        "top4_rate": sum(rank <= 4 for rank in ranks) / len(ranks),
        "first_place_rate": sum(rank == 1 for rank in ranks) / len(ranks),
        "decisions": [r["decisions"] for r in records],
        "truncated_combats": sum(r["truncated_combats"] for r in records),
    }


def train_one(name, steps, seed, base, engine):
    import torch
    from sb3_contrib import MaskablePPO
    from .env import TavernEnv
    from .model import TavernExtractor
    torch.set_num_threads(2)
    dest = base / name / "model.zip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    env = TavernEnv(seed=seed)
    try:
        model = MaskablePPO(
            "MultiInputPolicy", env, device="cpu", seed=seed, verbose=0,
            n_steps=128, batch_size=64, n_epochs=4, gamma=0.99,
            gae_lambda=0.95, learning_rate=3e-4, ent_coef=VARIANTS[name],
            policy_kwargs={
                "features_extractor_class": TavernExtractor,
                "features_extractor_kwargs": {"features_dim": 256},
                "net_arch": {"pi": [128], "vf": [128]},
            })
        model.learn(total_timesteps=steps)
        if model.num_timesteps != steps:
            raise RuntimeError("PPO training did not consume requested steps")
        model.save(str(dest))
    finally:
        env.close()
    metadata = {
        "name": name, "ent_coef": VARIANTS[name],
        "seed": seed, "steps": int(model.num_timesteps),
        "engine": engine, "path": str(dest),
        "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
        "n_steps": 128, "batch_size": 64, "n_epochs": 4,
        "learning_rate": 3e-4, "gamma": 0.99, "gae_lambda": 0.95,
    }
    (dest.parent / "model.metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def run_experiment(session_id, steps, train_seed, start_seed, games, base_sha):
    from .canary import run
    engine = verify_engine()
    model_root = Path("checkpoints") / session_id
    models = {name: train_one(name, steps, train_seed, model_root, engine)
              for name in VARIANTS}
    receipts = {name: [] for name in ("baseline", "zero", "regularized")}
    receipt_dir = Path("experiments") / session_id
    receipt_dir.mkdir(parents=True, exist_ok=True)
    for i in range(games):
        seed = start_seed + i
        for name in receipts:
            model_path = models[name]["path"] if name in models else None
            record = run(seed, session_id, "model" if model_path else "baseline", model_path)
            record["variant"] = name
            record["policy_version"] = "entropy-probe-v1" if model_path else "baseline-v0"
            record["training_steps"] = steps if model_path else 0
            record["training_seed"] = train_seed if model_path else None
            validate(record)
            receipt_name = ("001-" + str(seed) + ".json"
                            if name == "regularized" and i == 0
                            else name + "-" + str(seed) + ".json")
            (receipt_dir / receipt_name).write_text(
                json.dumps(record, indent=2), encoding="utf-8")
            receipts[name].append(record)
    report = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id, "base_main_sha": base_sha,
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "workflow_source_sha": os.environ.get("GITHUB_SHA"),
        "environment": "TavernGym", "engine": engine,
        "training_seed": train_seed, "steps_per_variant": steps,
        "total_training_steps": steps * 2,
        "eval_start_seed": start_seed, "games_per_variant": games,
        "models": models,
        "results": {name: aggregate(rows) for name, rows in receipts.items()},
        "limitation": "Exploratory N<=3; not evidence of an improvement or Arena Elo.",
    }
    report_dir = Path("reports") / session_id
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "entropy-comparison.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "report": str(report_dir / "entropy-comparison.json"),
        "training_steps": report["total_training_steps"],
        "ranks": {k: v["placements"] for k, v in report["results"].items()},
        "first_receipt": str(receipt_dir / ("001-" + str(start_seed) + ".json")),
    }))
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--steps", type=int, default=128)
    parser.add_argument("--train-seed", type=int, default=70141)
    parser.add_argument("--start-seed", type=int, default=31041)
    parser.add_argument("--games", type=int, default=2)
    parser.add_argument("--base-sha", required=True)
    args = parser.parse_args()
    if not args.session_id.startswith("s-") or "/" in args.session_id:
        parser.error("Invalid session id")
    if args.steps not in (128, 256, 512) or not 1 <= args.games <= 3:
        parser.error("Budget: 128/256/512 steps, 1..3 games per arm")
    run_experiment(args.session_id, args.steps, args.train_seed,
                   args.start_seed, args.games, args.base_sha)


if __name__ == "__main__":
    main()
