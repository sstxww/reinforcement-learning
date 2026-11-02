"""Single-seed, bounded architecture ablation on genuine TavernGym MaskablePPO."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from sb3_contrib import MaskablePPO

from .compact_model import CompactTavernExtractor
from .contract import verify_engine
from .env import TavernEnv
from .model import TavernExtractor


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _train_variant(name: str, extractor, features_dim: int, *,
                   steps: int, seed: int, output: Path, engine: dict) -> dict:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    env = TavernEnv(seed=seed)
    try:
        obs, _ = env.reset(seed=seed)
        mask = env.action_masks()
        if obs["features"].shape != (4017,) or obs["cards"].shape != (447,):
            raise ValueError("Unexpected observation contract")
        if mask.shape != (245,) or not mask.any():
            raise ValueError("Missing or malformed legal action mask")

        started = time.perf_counter()
        model = MaskablePPO(
            "MultiInputPolicy", env, device="cpu", verbose=0, seed=seed,
            n_steps=128, batch_size=64, n_epochs=4,
            gamma=0.99, gae_lambda=0.95,
            learning_rate=3e-4, ent_coef=0.01,
            policy_kwargs={
                "features_extractor_class": extractor,
                "features_extractor_kwargs": {"features_dim": features_dim},
                "net_arch": {"pi": [128], "vf": [128]},
            },
        )
        init_seconds = time.perf_counter() - started
        parameter_count = sum(p.numel() for p in model.policy.parameters())
        extractor_parameters = sum(
            p.numel() for p in model.policy.features_extractor.parameters()
        )

        started = time.perf_counter()
        model.learn(total_timesteps=steps, reset_num_timesteps=False)
        learn_seconds = time.perf_counter() - started
        if int(model.num_timesteps) != steps:
            raise AssertionError("Mismatch between requested and actual train steps")

        output.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(output))
        if not output.is_file():
            raise FileNotFoundError(f"Checkpoint not saved: {output}")
        metadata = {
            "schema": 1, "engine": engine, "total_timesteps": int(model.num_timesteps),
            "training_seed": seed, "algorithm": "MaskablePPO",
            "extractor": extractor.__name__, "features_dim": features_dim,
            "policy_parameters": parameter_count,
            "source": "independent architecture ablation; no pretrained weights",
        }
        output.with_suffix(".metadata.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )
        return {
            "variant": name, "checkpoint": str(output),
            "sha256": _sha256(output), "steps": int(model.num_timesteps),
            "seed": seed, "init_seconds": round(init_seconds, 3),
            "learn_seconds": round(learn_seconds, 3),
            "policy_parameters": parameter_count,
            "extractor_parameters": extractor_parameters,
            "initial_legal_actions": int(mask.sum()),
        }
    finally:
        env.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=128)
    parser.add_argument("--seed", type=int, default=261102)
    parser.add_argument("--out", type=Path, required=True)
    a = parser.parse_args()
    if a.steps < 128 or a.steps > 512 or a.steps % 128 != 0:
        raise ValueError("steps must be a multiple of 128 in [128,512]")
    a.out.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(2)
    engine = verify_engine()
    control = _train_variant(
        "control-original", TavernExtractor, 256,
        steps=a.steps, seed=a.seed, output=a.out / "control.zip", engine=engine,
    )
    candidate = _train_variant(
        "candidate-compact", CompactTavernExtractor, 192,
        steps=a.steps, seed=a.seed, output=a.out / "candidate.zip", engine=engine,
    )
    report = {
        "schema": 1, "experiment": "compact-extractor-ablation-001",
        "engine": engine, "steps_per_variant": a.steps,
        "actual_total_steps": control["steps"] + candidate["steps"],
        "control": control, "candidate": candidate,
        "policy_parameter_reduction_fraction": round(
            1 - candidate["policy_parameters"] / control["policy_parameters"], 6
        ),
        "wallclock_learn_speedup_fraction": round(
            1 - candidate["learn_seconds"] / control["learn_seconds"], 6
        ) if control["learn_seconds"] > 0 else None,
        "important": "One timing sample each; no claim of improved win rate.",
    }
    (a.out / "training-metrics.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
