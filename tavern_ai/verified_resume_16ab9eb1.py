"""V5 fail-closed Release-registry resume gateway (isolated integration candidate).

Preflight is offline, uses only pinned main registry and local downloaded assets.
It is NOT proof of a load, PPO continuation, a full game, or model strength.
The optional execution path never writes the source checkpoint or Champion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .checkpoint_preflight import audit_archive
from .registry_integrity import validate_registry


def checked_bundle(registry: Path, model_id: str, checkpoint: Path, metadata: Path) -> dict:
    """Bind archive bytes to canonical registry model ID and exact training steps."""
    registry, checkpoint, metadata = Path(registry), Path(checkpoint), Path(metadata)
    data = json.loads(registry.read_text(encoding="utf-8"))
    validate_registry(data)
    row = next((item for item in data["candidates"] if item["id"] == model_id), None)
    if row is None:
        raise ValueError("Model ID not present in verified registry inventory")
    if row["role"] != "candidate_unpromoted":
        raise ValueError("Only unpromoted candidates may be preflighted")
    checked = audit_archive(checkpoint, metadata, row["checkpoint_sha256"])
    if checked["total_timesteps"] != row["training_steps"]:
        raise ValueError("Checkpoint training-step mismatch with trusted registry")
    return {
        "schema": 1,
        "source_model_id": model_id,
        "source_release": row["release_url"],
        "source_sha256": checked["sha256"],
        "source_training_steps": checked["total_timesteps"],
        "archive_integrity": "passed",
        "model_load": "not_tested",
        "optimizer_resume": "not_tested",
        "complete_match": "not_tested",
        "competitive_gain": "not_tested",
        "champion_promoted": False,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resume_from_checked_release(
    registry: Path, model_id: str, checkpoint: Path, metadata: Path,
    out: Path, steps: int, seed: int,
) -> dict:
    """Optional explicit bounded PPO continuation, with immutable parent lineage."""
    checkpoint, metadata, out = Path(checkpoint), Path(metadata), Path(out)
    if type(steps) is not int or not 128 <= steps <= 20000:
        raise ValueError("Explicit bounded PPO steps must be 128..20000")
    if type(seed) is not int or seed < 0:
        raise ValueError("Seed must be a nonnegative integer")
    if out.suffix != ".zip" or checkpoint.suffix != ".zip":
        raise ValueError("Require checkpoint and output .zip paths")
    if metadata.resolve() != checkpoint.with_suffix(".metadata.json").resolve():
        raise ValueError("Metadata must be the exact sidecar consumed by the trainer")
    child_meta = out.with_suffix(".metadata.json")
    lineage_path = out.with_suffix(".lineage.json")
    if checkpoint.resolve() == out.resolve():
        raise ValueError("Never overwrite the sole source checkpoint")
    if any(p.exists() for p in (out, child_meta, lineage_path)):
        raise FileExistsError("Refuse overwrite of an existing checkpoint or provenance")
    parent = checked_bundle(registry, model_id, checkpoint, metadata)
    from .train import run
    result = run(steps=steps, seed=seed, model_out=out, resume=checkpoint)
    if not out.is_file() or not child_meta.is_file():
        raise RuntimeError("Trainer did not create checkpoint and metadata")
    child_sha = _sha256(out)
    checked = audit_archive(out, child_meta, child_sha)
    child_steps = checked["total_timesteps"]
    if child_steps < parent["source_training_steps"] + steps:
        raise ValueError("Trainer failed to advance the expected PPO step count")
    if result["total_timesteps"] != child_steps:
        raise ValueError("Trainer return and archived metadata disagree")
    # Recheck immutable parent after optimizer continuation.
    if _sha256(checkpoint) != parent["source_sha256"]:
        raise ValueError("Source checkpoint changed during continuation")
    lineage = {
        "schema": 1, "status": "unpromoted_challenger",
        "parent_model_id": model_id, "parent_sha256": parent["source_sha256"],
        "parent_training_steps": parent["source_training_steps"],
        "checkpoint_sha256": child_sha, "total_timesteps": child_steps,
        "requested_additional_steps": steps, "actual_additional_steps": child_steps - parent["source_training_steps"],
        "training_seed": seed, "archive_integrity": "passed",
        "optimizer_continuation": "completed", "complete_match": "not_tested",
        "heldout_evaluation": "not_tested", "durable_release": "not_published",
        "champion_promoted": False,
    }
    with lineage_path.open("x", encoding="utf-8") as handle:
        json.dump(lineage, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return lineage


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    p.add_argument("--model-id", required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--out", type=Path)
    p.add_argument("--steps", type=int, default=128)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--execute-resume", action="store_true", help="Explicitly spend CPU PPO budget")
    args = p.parse_args()
    if args.execute_resume:
        if args.out is None:
            p.error("--execute-resume requires --out")
        result = resume_from_checked_release(
            args.registry, args.model_id, args.checkpoint, args.metadata,
            args.out, args.steps, args.seed,
        )
    else:
        result = checked_bundle(args.registry, args.model_id, args.checkpoint, args.metadata)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
