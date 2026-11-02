"""Incremental mask-aware PPO training with hash-checked, staged checkpoint resume."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .checkpoint_integrity import save_checkpoint, verify_checkpoint
from .contract import verify_engine
from .env import TavernEnv


def run(steps: int, seed: int, model_out: Path, resume: Path | None = None):
    from sb3_contrib import MaskablePPO
    from .model import TavernExtractor
    if steps < 128:
        raise ValueError("steps must be >=128")
    engine = verify_engine()
    # Verify bytes and exact observation/card contract *before* deserializing Torch.
    if resume is not None:
        previous = verify_checkpoint(resume, expected_engine=engine)
    else:
        previous = None
    env = TavernEnv(seed=seed)
    try:
        if resume is not None:
            model = MaskablePPO.load(str(resume), env=env, device="cpu")
            if int(model.num_timesteps) != previous["total_timesteps"]:
                raise ValueError("Saved training steps disagree with model parameters")
        else:
            model = MaskablePPO(
                "MultiInputPolicy", env, device="cpu", verbose=1, seed=seed,
                n_steps=128, batch_size=64, n_epochs=4, gamma=0.99,
                gae_lambda=0.95, learning_rate=3e-4, ent_coef=0.01,
                policy_kwargs={"features_extractor_class": TavernExtractor,
                               "features_extractor_kwargs": {"features_dim": 256},
                               "net_arch": {"pi": [128], "vf": [128]}},
            )
        model.learn(total_timesteps=steps, reset_num_timesteps=False)
        if previous is not None and int(model.num_timesteps) <= previous["total_timesteps"]:
            raise RuntimeError("Resume did not advance total training steps")
        meta = {
            "schema": 1, "engine": engine, "total_timesteps": int(model.num_timesteps),
            "training_seed": seed, "algorithm": "MaskablePPO",
            "notes": "V1 CPU single-seat vs seven scripted bots",
        }
        if previous is not None:
            meta["parent_checkpoint_sha256"] = previous["checkpoint_sha256"]
            meta["parent_total_timesteps"] = previous["total_timesteps"]
        return save_checkpoint(model, model_out, meta)
    finally:
        env.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=2048)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=Path("checkpoints/model.zip"))
    p.add_argument("--resume", type=Path)
    a = p.parse_args()
    print(json.dumps(run(a.steps, a.seed, a.out, a.resume), ensure_ascii=False))


if __name__ == "__main__":
    main()
