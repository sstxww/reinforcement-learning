"""Isolated, bounded entropy ablation on the pinned TavernGym engine.

Reference and candidate share observations, train seed, budget, and network;
only entropy regularization differs.  This does not change shared train.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path

import numpy as np

from .guarded_match import run as play
from .contract import ACTIONS, CARDS, FEATURES, verify_engine


def summarize(receipts: list[dict]) -> dict:
    ranks = [int(item["placements"][0]) for item in receipts]
    if not ranks:
        raise ValueError("at least one full match is required")
    return {
        "games": len(ranks),
        "seat0_placements": ranks,
        "mean_placement": statistics.mean(ranks),
        "top4_rate": sum(p <= 4 for p in ranks) / len(ranks),
        "first_rate": sum(p == 1 for p in ranks) / len(ranks),
        "mean_decisions": statistics.mean(item["decisions"] for item in receipts),
        "illegal_actions": 0,  # canary raises before stepping if mask excludes action
        "protective_truncations": sum(item["truncated_combats"] for item in receipts),
    }


def execute(agent_id: str, train_seed: int, eval_seeds: tuple[int, ...],
            steps: int, output_dir: Path) -> dict:
    import torch
    from sb3_contrib import MaskablePPO
    from .env import TavernEnv
    from .model import TavernExtractor
    from .validate_receipt import validate

    if not agent_id.startswith("s-") or "/" in agent_id:
        raise ValueError("isolated session id required")
    if steps < 128 or steps % 128:
        raise ValueError("steps must be a positive multiple of 128")
    if not eval_seeds or len(set(eval_seeds)) != len(eval_seeds):
        raise ValueError("unique held-out evaluation seeds required")
    if train_seed in eval_seeds:
        raise ValueError("training seed cannot be an evaluation seed")

    torch.set_num_threads(2)
    engine = verify_engine()
    output_dir.mkdir(parents=True, exist_ok=True)
    receipt_dir = Path("experiments") / agent_id
    receipt_dir.mkdir(parents=True, exist_ok=True)
    records = {}
    for variant, entropy_coef in (("reference", 0.01), ("candidate", 0.04)):
        env = TavernEnv(seed=train_seed)
        try:
            obs, _ = env.reset(seed=train_seed)
            mask = env.action_masks()
            if obs["features"].shape != (FEATURES,) or obs["cards"].shape != (CARDS,):
                raise AssertionError("observation contract changed")
            if mask.shape != (ACTIONS,) or mask.dtype != np.bool_ or not mask.any():
                raise AssertionError("legal action-mask contract changed")
            model = MaskablePPO(
                "MultiInputPolicy", env, seed=train_seed, device="cpu", verbose=0,
                n_steps=128, batch_size=64, n_epochs=4, gamma=0.99,
                gae_lambda=0.95, learning_rate=3e-4, ent_coef=entropy_coef,
                policy_kwargs={
                    "features_extractor_class": TavernExtractor,
                    "features_extractor_kwargs": {"features_dim": 256},
                    "net_arch": {"pi": [128], "vf": [128]},
                },
            )
            model.learn(total_timesteps=steps)
            actual_steps = int(model.num_timesteps)
            checkpoint = output_dir / f"{variant}.zip"
            model.save(str(checkpoint))
            sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
            del model
        finally:
            env.close()

        receipts = []
        for seed in eval_seeds:
            receipt = play(seed=seed, agent_id=agent_id, policy="model",
                           model_path=str(checkpoint))
            validate(receipt)
            filename = (f"001-{seed}.json" if variant == "candidate" and seed == eval_seeds[0]
                        else f"{variant}-{seed}.json")
            (receipt_dir / filename).write_text(
                json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            receipts.append(receipt)
        records[variant] = {
            "entropy_coef": entropy_coef,
            "training_steps": actual_steps,
            "checkpoint_sha256": sha,
            "checkpoint": str(checkpoint),
            "evaluation": summarize(receipts),
        }

    report = {
        "schema": 1, "agent_id": agent_id, "hypothesis":
        "0.04 entropy improves paired held-out placement over 0.01 after a fixed small PPO budget",
        "engine": engine, "observation_contract":
        {"features": FEATURES, "cards": CARDS, "actions": ACTIONS},
        "train_seed": train_seed, "eval_seeds": list(eval_seeds),
        "steps_requested_per_arm": steps,
        "arms": records,
        "candidate_minus_reference_mean_placement":
        records["candidate"]["evaluation"]["mean_placement"]
        - records["reference"]["evaluation"]["mean_placement"],
        "interpretation": "Exploratory tiny-sample ablation; not a strength claim.",
        "storage": "Session-scoped GitHub Actions artifact; expires after retention period.",
    }
    metrics_path = Path("research") / "sessions" / agent_id / "metrics-001.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--train-seed", type=int, default=77331)
    parser.add_argument("--eval-seeds", type=int, nargs="+", default=[61001, 61002])
    parser.add_argument("--steps", type=int, default=256)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    execute(args.agent_id, args.train_seed, tuple(args.eval_seeds),
            args.steps, args.output_dir)


if __name__ == "__main__":
    main()
