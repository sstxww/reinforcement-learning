"""V5 isolated Release-backed PPO resume, preserving full checkpoint provenance.

No champion promotion. Actual inference/full-match validation is a separate gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from tavern_ai.checkpoint_preflight import audit_archive
from tavern_ai.contract import CATALOG_SHA256, PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def registry_source(registry: Path) -> dict:
    catalog = json.loads(registry.read_text(encoding="utf-8"))
    latest = catalog.get("latest")
    if not isinstance(latest, dict):
        raise ValueError("Registry has no Latest checkpoint")
    if latest.get("role") != "latest_experimental_unpromoted":
        raise ValueError("Unexpected source model role; fail closed")
    if latest.get("durable_storage") != "github_release":
        raise ValueError("No trusted persistent Release checkpoint")
    if latest.get("model_asset") != "model.zip" or latest.get("metadata_asset") != "model.metadata.json":
        raise ValueError("Unexpected Release asset names")
    if not isinstance(latest.get("checkpoint_sha256"), str):
        raise ValueError("Registry missing trusted SHA256")
    return latest


def compatible_metadata(parent: dict, updated: dict, *, digest: str, added_steps: int,
                        parent_id: str, parent_digest: str) -> dict:
    previous = parent.get("total_timesteps")
    current = updated.get("total_timesteps")
    if type(previous) is not int or type(current) is not int:
        raise ValueError("Checkpoint step count must be integer")
    if type(added_steps) is not int or added_steps <= 0 or current != previous + added_steps:
        raise ValueError("Resume did not advance exactly the requested training steps")
    if updated.get("algorithm") != "MaskablePPO" or updated.get("engine") != parent.get("engine"):
        raise ValueError("Trainer changed engine or algorithm")
    engine = parent["engine"]
    return {
        "schema": 2,
        "algorithm": "MaskablePPO",
        "engine": engine,
        "compatibility": {
            "engine": engine,
            "catalog_sha256": CATALOG_SHA256,
            "ruleset_id": RULESET_ID,
            "patch_sha256": PATCH_SHA256,
            "upstream_commit": UPSTREAM_COMMIT,
        },
        "total_timesteps": current,
        "increment_timesteps": added_steps,
        "training_seed": updated.get("training_seed"),
        "checkpoint_sha256": digest,
        "parent_model_id": parent_id,
        "parent_sha256": parent_digest,
        "source_commit": os.environ.get("GITHUB_SHA", ""),
        "role": "candidate_unpromoted",
        "notes": "Release-backed bounded PPO continuation; no strength claim",
    }


def resume(*, registry: Path, source: Path, source_metadata: Path,
           output: Path, steps: int, seed: int, report: Path) -> dict:
    if steps != 128:
        raise ValueError("This isolated audit limits training to exactly 128 steps")
    if source.resolve() == output.resolve():
        raise ValueError("Never overwrite the immutable source checkpoint")
    if output.exists() or output.with_suffix(".metadata.json").exists():
        raise FileExistsError("Output checkpoint already exists")
    latest = registry_source(registry)
    old_digest = latest["checkpoint_sha256"]
    verified = audit_archive(source, source_metadata, old_digest)
    parent = json.loads(source_metadata.read_text(encoding="utf-8"))
    if parent["total_timesteps"] != latest["training_steps"]:
        raise ValueError("Registry/source step count mismatch")
    # Imported here so metadata tests remain CPU-only and do not need Torch/SB3.
    from tavern_ai.train import run
    raw = run(steps, seed, output, source)
    new_digest = digest_file(output)
    metadata = compatible_metadata(parent, raw, digest=new_digest, added_steps=steps,
                                   parent_id=latest["id"], parent_digest=old_digest)
    meta_path = output.with_suffix(".metadata.json")
    temp = meta_path.with_suffix(meta_path.suffix + ".tmp")
    temp.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    temp.replace(meta_path)
    audited = audit_archive(output, meta_path, new_digest)
    result = {
        "source_id": latest["id"],
        "source_sha256": old_digest,
        "source_preflight": verified["archive_integrity"],
        "source_schema": verified["checkpoint_metadata_schema"],
        "new_sha256": new_digest,
        "new_schema": audited["checkpoint_metadata_schema"],
        "previous_timesteps": parent["total_timesteps"],
        "added_timesteps": steps,
        "total_timesteps": metadata["total_timesteps"],
        "new_archive_preflight": audited["archive_integrity"],
        "optimizer_state_present": True,
        "full_match_verified": False,
        "competitive_improvement_verified": False,
        "promotion_allowed": False,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=128)
    parser.add_argument("--seed", type=int, default=99372431)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(resume(registry=args.registry, source=args.source,
                             source_metadata=args.source_metadata, output=args.out,
                             steps=args.steps, seed=args.seed, report=args.report),
                     sort_keys=True))


if __name__ == "__main__":
    main()
