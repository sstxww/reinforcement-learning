"""Isolated paired reward-scale experiment for TavernGym 1.1.0.

This module intentionally does not change the shared training entry point.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

import gymnasium as gym
import numpy as np

from .contract import verify_engine
from .env import TavernEnv


class RewardScale(gym.Wrapper):
    """Preserve legal-action masks while scaling the scalar training reward."""

    def __init__(self, env: gym.Env, scale: float):
        if not math.isfinite(scale) or scale <= 0:
            raise ValueError("Reward scale must be finite and strictly positive")
        super().__init__(env)
        self.scale = float(scale)

    def action_masks(self):
        return self.env.action_masks()

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        return obs, float(reward) * self.scale, terminated, truncated, info


def train_arm(*, seed: int, steps: int, scale: float, out: Path, metrics: Path) -> dict:
    """Train one independently seeded MaskablePPO model, save a bounded receipt."""
    from sb3_contrib import MaskablePPO
    from stable_baselines3.common.callbacks import BaseCallback
    from stable_baselines3.common.logger import configure
    from .model import TavernExtractor

    if steps < 128 or steps % 128:
        raise ValueError("steps must be >=128 and divisible by 128")
    engine = verify_engine()
    env = RewardScale(TavernEnv(seed=seed), scale)

    class RewardObserver(BaseCallback):
        def __init__(self):
            super().__init__(verbose=0)
            self.values = []

        def _on_step(self) -> bool:
            self.values.extend(float(x) for x in np.asarray(self.locals["rewards"]).ravel())
            return True

    observer = RewardObserver()
    out.parent.mkdir(parents=True, exist_ok=True)
    metrics.parent.mkdir(parents=True, exist_ok=True)
    log_dir = metrics.parent / ("ppo-" + out.stem)
    model = MaskablePPO(
        "MultiInputPolicy", env, device="cpu", verbose=0, seed=seed,
        n_steps=128, batch_size=64, n_epochs=4, gamma=0.99,
        gae_lambda=0.95, learning_rate=3e-4, ent_coef=0.01,
        policy_kwargs={
            "features_extractor_class": TavernExtractor,
            "features_extractor_kwargs": {"features_dim": 256},
            "net_arch": {"pi": [128], "vf": [128]},
        },
    )
    model.set_logger(configure(str(log_dir), ["json"]))
    try:
        model.learn(total_timesteps=steps, reset_num_timesteps=False, callback=observer)
        actual_steps = int(model.num_timesteps)
        model.save(str(out))
        digest = hashlib.sha256(out.read_bytes()).hexdigest()
        progress = log_dir / "progress.json"
        summaries = [json.loads(s) for s in progress.read_text().splitlines() if s.strip()] if progress.exists() else []
        last = summaries[-1] if summaries else {}
        result = {
            "schema": 1,
            "session_id": "s-20261102-14ce98f3",
            "variant": "raw" if scale == 1 else "scaled",
            "reward_scale": scale,
            "seed": seed,
            "requested_timesteps": steps,
            "actual_timesteps": actual_steps,
            "engine": engine,
            "training_algorithm": "MaskablePPO",
            "model_sha256": digest,
            "model_artifact_path": str(out),
            "commit": os.getenv("GITHUB_SHA", ""),
            "observed_rewards": len(observer.values),
            "mean_training_reward": float(np.mean(observer.values)) if observer.values else None,
            "std_training_reward": float(np.std(observer.values)) if observer.values else None,
            "train_value_loss": last.get("train/value_loss"),
            "train_approx_kl": last.get("train/approx_kl"),
            "train_explained_variance": last.get("train/explained_variance"),
            "log_records": len(summaries),
        }
        metrics.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False), flush=True)
        return result
    finally:
        env.close()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--scale", type=float, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--steps", type=int, default=256)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--metrics", type=Path, required=True)
    a = p.parse_args()
    train_arm(seed=a.seed, steps=a.steps, scale=a.scale, out=a.out, metrics=a.metrics)


if __name__ == "__main__":
    main()
