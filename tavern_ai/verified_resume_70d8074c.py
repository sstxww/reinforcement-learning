"""V5 isolated, fail-closed Release -> resumed-PPO entrypoint.

Compose the *existing* canonical registry, two-asset Release digest checker,
strict SB3 archive preflight and the existing training implementation.
This is an opt-in bounded integration test, not a replacement for main/train.yml.
No model is promoted, and no unverified fallback to random initialization exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .checkpoint_preflight import audit_archive, probe_inference
from .release_asset_verifier import validate_asset_index, verify_local

MAX_STEPS = 512
SOURCE_REGISTRY = Path("models/registry.json")
ASSET_DIGESTS = Path("models/release_asset_digests.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_budget(steps: int) -> None:
    if type(steps) is not int or steps < 128 or steps > MAX_STEPS or steps % 128:
        raise ValueError("Smoke resume must use 128..512 steps in 128-step blocks")


def verified_source(
    model_id: str, weights: Path, metadata: Path,
    registry_path: Path = SOURCE_REGISTRY,
    asset_index_path: Path = ASSET_DIGESTS,
    *, probe: bool = False,
) -> dict:
    """Reject unregistered/altered assets before ANY PPO deserialization."""
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    index = json.loads(asset_index_path.read_text(encoding="utf-8"))
    validate_asset_index(index, registry)
    candidate = next((x for x in registry["candidates"] if x["id"] == model_id), None)
    if candidate is None or candidate.get("role") != "candidate_unpromoted":
        raise ValueError("Unknown or promoted model ID; explicit unpromoted ID required")
    if registry.get("best") is not None or registry.get("champion") is not None:
        raise ValueError("Unexpected champion state: fail closed")
    if weights.name != "model.zip" or metadata.name != "model.metadata.json":
        raise ValueError("Release asset names must be canonical")
    verified = verify_local(index, registry, model_id, weights, metadata, check_load=False)
    archive = audit_archive(weights, metadata, candidate["checkpoint_sha256"])
    if archive["total_timesteps"] != candidate["training_steps"]:
        raise ValueError("Checkpoint and canonical registry timestep mismatch")
    if probe:
        probe_inference(weights)  # Real engine, MaskablePPO.load, and one legal action.
    return {
        "model_id": model_id,
        "source_sha256": candidate["checkpoint_sha256"],
        "source_steps": candidate["training_steps"],
        "source_assets_verified": bool(
            verified["weight_bytes_sha256_verified"]
            and verified["metadata_bytes_sha256_verified"]
        ),
        "source_archive_integrity": archive["archive_integrity"],
        "source_engine_contract_verified": True,
        "source_one_action_inference": bool(probe),
    }


def resume_once(
    model_id: str, weights: Path, metadata: Path, steps: int, seed: int,
    output: Path, report: Path, *, probe: bool = False,
) -> dict:
    validate_budget(steps)
    weights = weights.resolve()
    metadata = metadata.resolve()
    output = output.resolve()
    report = report.resolve()
    if output == weights or output == metadata or output.is_file():
        raise ValueError("Output must be a new, separate checkpoint")
    if output.with_suffix(".metadata.json").is_file() or report.is_file():
        raise ValueError("Output metadata/report already exists; refusing overwrite")
    if not weights.is_file() or not metadata.is_file():
        raise FileNotFoundError("Both Release assets are required")
    # The existing trainer derives its metadata with weights.with_suffix().
    if metadata != weights.with_suffix(".metadata.json"):
        raise ValueError("Source metadata must be adjacent to source model.zip")
    source = verified_source(model_id, weights, metadata, probe=probe)
    # Never run train() if even one preflight gate fails.
    from .train import run as train
    result = train(steps=steps, seed=seed, model_out=output, resume=weights)
    expected = source["source_steps"] + steps
    if result.get("total_timesteps") != expected:
        raise ValueError("Real PPO continuation did not advance exact cumulative steps")
    if not output.is_file():
        raise RuntimeError("PPO did not produce a checkpoint")
    output_meta = output.with_suffix(".metadata.json")
    if not output_meta.is_file():
        raise RuntimeError("PPO did not produce resumability metadata")
    new_sha = sha256(output)
    if new_sha == source["source_sha256"]:
        raise ValueError("Training output is byte-identical to source")
    new_archive = audit_archive(output, output_meta, new_sha)
    if new_archive["total_timesteps"] != expected:
        raise ValueError("Output archive/metadata step mismatch")
    # Do not assume producing a ZIP is equivalent to inference.
    if probe:
        probe_inference(output)
    summary = {
        "schema": 1,
        "session_id": "s-20261102-70d8074c",
        "parent": source,
        "new_sha256": new_sha,
        "new_metadata_sha256": sha256(output_meta),
        "source_steps": source["source_steps"],
        "new_steps": expected,
        "actual_additional_steps": expected - source["source_steps"],
        "seed": seed,
        "optimizer_continuation_executed": True,
        "new_archive_integrity": new_archive["archive_integrity"],
        "new_one_action_inference": bool(probe),
        "full_eight_seat_match": "not_tested_by_this_entrypoint",
        "competitive_improvement": "not_claimed",
        "champion_promoted": False,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=128)
    parser.add_argument("--seed", type=int, default=73021)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--probe-inference", action="store_true")
    args = parser.parse_args()
    print(json.dumps(resume_once(
        args.model_id, args.weights, args.metadata, args.steps, args.seed,
        args.out, args.report, probe=args.probe_inference
    ), sort_keys=True))


if __name__ == "__main__":
    main()
