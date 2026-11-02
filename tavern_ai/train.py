"""Incremental mask-aware PPO with staged, SHA-bound checkpoint writes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .checkpoint_writer import save_checkpoint, sha256_file, verify_resume_digest
from .contract import verify_engine
from .env import TavernEnv


def require_verified_resume(resume: Path, metadata: dict) -> str:
    """Reject SHA-less legacy restarts before deserializing a PPO checkpoint.

    A metadata self-digest detects corruption, but callers still need trusted
    Release/registry provenance; this is not a Champion or strength gate.
    """
    if not verify_resume_digest(resume, metadata):
        raise ValueError(
            "Refusing SHA-less legacy PPO resume: verify a pinned Release "
            "and migrate to SHA-bound checkpoint metadata first"
        )
    return sha256_file(resume)


def run(steps: int, seed: int, model_out: Path, resume: Path | None = None):
    from sb3_contrib import MaskablePPO
    from .model import TavernExtractor

    if steps < 128:
        raise ValueError("steps must be >=128")
    engine = verify_engine()
    env = TavernEnv(seed=seed)
    try:
        parent_sha256 = None
        if resume is not None:
            if not resume.is_file():
                raise FileNotFoundError(resume)
            meta_path = resume.with_suffix(".metadata.json")
            if not meta_path.is_file():
                raise ValueError("Missing checkpoint compatibility metadata")
            prev = json.loads(meta_path.read_text(encoding="utf-8"))
            if not isinstance(prev, dict) or prev.get("engine") != engine:
                raise ValueError("Checkpoint engine or card vocabulary mismatch")
            parent_sha256 = require_verified_resume(resume, prev)
            model = MaskablePPO.load(str(resume), env=env, device="cpu")
            if type(prev.get("total_timesteps")) is not int or (
                int(model.num_timesteps) != prev["total_timesteps"]
            ):
                raise ValueError("Saved model and metadata training-step counters differ")
        else:
            model = MaskablePPO(
                "MultiInputPolicy", env, device="cpu", verbose=1, seed=seed,
                n_steps=128, batch_size=64, n_epochs=4,
                gamma=0.99, gae_lambda=0.95, learning_rate=3e-4,
                ent_coef=0.01,
                policy_kwargs={
                    "features_extractor_class": TavernExtractor,
                    "features_extractor_kwargs": {"features_dim": 256},
                    "net_arch": {"pi": [128], "vf": [128]},
                },
            )
        model.learn(total_timesteps=steps, reset_num_timesteps=False)
        meta = {
            "schema": 1,
            "engine": engine,
            "total_timesteps": int(model.num_timesteps),
            "training_seed": seed,
            "algorithm": "MaskablePPO",
            "notes": "V1 CPU single-seat vs seven scripted bots",
        }
        if parent_sha256 is not None:
            meta["parent_checkpoint_sha256"] = parent_sha256
        return save_checkpoint(model, model_out, meta)
    finally:
        env.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=2048)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("checkpoints/model.zip"))
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.steps, args.seed, args.out, args.resume), ensure_ascii=False))


if __name__ == "__main__":
    main()
