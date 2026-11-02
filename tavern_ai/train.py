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


def verify_parent_before_load(engine: dict, parent: dict) -> None:
    """Fail closed on incompatible resume metadata before PPO deserialization/learn.

    This preflight is deliberately repeated by build_checkpoint_metadata after
    training; the post-save gate alone cannot protect expensive GPU/CPU steps.
    A bound checkpoint digest is checked separately before MaskablePPO.load.
    """
    if not isinstance(parent, dict) or parent.get("engine") != engine:
        raise ValueError("Incompatible parent engine before PPO load")
    previous = parent.get("total_timesteps")
    if type(previous) is not int or previous < 1:
        raise ValueError("Invalid parent total_timesteps before PPO load")
    schema = parent.get("schema")
    if schema == 1:
        return
    if schema != 2:
        raise ValueError("Unknown parent checkpoint schema before PPO load")
    from .contract import CATALOG_SHA256, PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT
    expected = {
        "engine": engine, "catalog_sha256": CATALOG_SHA256,
        "patch_sha256": PATCH_SHA256, "ruleset_id": RULESET_ID,
        "upstream_commit": UPSTREAM_COMMIT,
    }
    if parent.get("compatibility") != expected:
        raise ValueError("Parent schema-2 compatibility provenance mismatch before PPO load")


def build_checkpoint_metadata(
    *, engine: dict, seed: int, total_timesteps: int,
    parent: dict | None = None, parent_sha256: str | None = None,
) -> dict:
    """Preserve schema-2 optimizer/engine provenance across actual PPO resumes.

    This is pure metadata construction, not evidence of completed training.
    The checkpoint writer binds the new child SHA256 after saving the ZIP.
    """
    if type(total_timesteps) is not int or total_timesteps < 1:
        raise ValueError("Invalid resumed training step counter")
    if (parent is None) != (parent_sha256 is None):
        raise ValueError("Parent metadata and verified parent digest must agree")
    meta = {
        "schema": 1, "engine": engine,
        "total_timesteps": total_timesteps,
        "training_seed": seed, "algorithm": "MaskablePPO",
        "notes": "CPU single-seat versus seven TavernGym scripted bots",
    }
    if parent is None:
        return meta
    if not isinstance(parent, dict) or parent.get("engine") != engine:
        raise ValueError("Incompatible parent engine")
    previous = parent.get("total_timesteps")
    if type(previous) is not int or previous < 1 or total_timesteps <= previous:
        raise ValueError("Missing or non-increasing cumulative PPO steps")
    from .checkpoint_writer import _SHA256
    if not isinstance(parent_sha256, str) or not _SHA256.fullmatch(parent_sha256):
        raise ValueError("Invalid verified parent checkpoint digest")
    meta["parent_checkpoint_sha256"] = parent_sha256
    if parent.get("schema") == 1:
        return meta
    if parent.get("schema") != 2:
        raise ValueError("Unknown parent checkpoint schema (refusing downgrade)")
    from .contract import CATALOG_SHA256, PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT
    expected = {
        "engine": engine, "catalog_sha256": CATALOG_SHA256,
        "patch_sha256": PATCH_SHA256, "ruleset_id": RULESET_ID,
        "upstream_commit": UPSTREAM_COMMIT,
    }
    if parent.get("compatibility") != expected:
        raise ValueError("Parent schema-2 compatibility provenance mismatch")
    meta["schema"] = 2
    meta["compatibility"] = expected
    meta["increment_timesteps"] = total_timesteps - previous
    return meta

def run(steps: int, seed: int, model_out: Path, resume: Path | None = None):
    from sb3_contrib import MaskablePPO
    from .model import TavernExtractor

    if steps < 128:
        raise ValueError("steps must be >=128")
    engine = verify_engine()
    env = TavernEnv(seed=seed)
    try:
        parent_sha256 = None
        prev = None
        if resume is not None:
            if not resume.is_file():
                raise FileNotFoundError(resume)
            meta_path = resume.with_suffix(".metadata.json")
            if not meta_path.is_file():
                raise ValueError("Missing checkpoint compatibility metadata")
            prev = json.loads(meta_path.read_text(encoding="utf-8"))
            if not isinstance(prev, dict) or prev.get("engine") != engine:
                raise ValueError("Checkpoint engine or card vocabulary mismatch")
            verify_parent_before_load(engine, prev)
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
        meta = build_checkpoint_metadata(
            engine=engine, seed=seed, total_timesteps=int(model.num_timesteps),
            parent=prev, parent_sha256=parent_sha256,
        )
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
