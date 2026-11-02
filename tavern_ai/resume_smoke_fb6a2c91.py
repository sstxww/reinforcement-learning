"""Fail-closed, 128-step Release-backed PPO resume smoke for one isolated V5 session.

This is NOT a stronger policy claim and never updates the shared registry or train.yml.
The caller supplies actual downloaded Release assets; no silent random restart.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .release_asset_verifier import verify_local
from .registry_integrity import validate_registry
from .contract import verify_engine
from .train import run as train_run

SOURCE_ID = "v5-s-20261102-68099929-1408-41428692617"
SESSION = "s-20261102-fb6a2c91"
SHA256 = re.compile(r"^[a-f0-9]{64}$")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def lineage_record(parent_id: str, parent_steps: int, parent_hash: str,
                   child_steps: int, child_hash: str, added: int) -> dict:
    """Ensure true cumulative learning; no fresh or unchanged checkpoint masquerade."""
    if not isinstance(parent_id, str) or not parent_id:
        raise ValueError("Missing parent model")
    if any(type(x) is not int or x < 1 for x in (parent_steps, child_steps, added)):
        raise ValueError("Invalid cumulative/incremental step count")
    if child_steps != parent_steps + added:
        raise ValueError("Resume did not advance the correct cumulative steps")
    if any(not isinstance(s, str) or not SHA256.fullmatch(s)
           for s in (parent_hash, child_hash)):
        raise ValueError("Missing model SHA256 provenance")
    if parent_hash == child_hash:
        raise ValueError("Resume produced unchanged checkpoint bytes")
    return {
        "schema": 1, "session_id": SESSION, "parent_model_id": parent_id,
        "parent_sha256": parent_hash, "child_sha256": child_hash,
        "parent_steps": parent_steps, "added_steps": added,
        "child_steps": child_steps, "state": "unpromoted_checkpoint",
        "model_only_full_match": "not_tested_by_this_function",
        "competitive_improvement": "not_established",
    }


def smoke(source: Path, dest: Path, lineage: Path, steps: int, seed: int,
          registry_path: Path, asset_index_path: Path) -> dict:
    """Hash-verify both source assets, load the existing PPO, continue and archive."""
    if steps != 128:
        raise ValueError("Only a bounded 128-step restore smoke is authorized")
    if source.resolve() == dest.resolve():
        raise ValueError("Never overwrite the sole parent Release asset")
    metadata = source.with_suffix(".metadata.json")
    canonical = json.loads(registry_path.read_text(encoding="utf-8"))
    index = json.loads(asset_index_path.read_text(encoding="utf-8"))
    validate_registry(canonical)
    parent = next((m for m in canonical["candidates"] if m["id"] == SOURCE_ID), None)
    if parent is None:
        raise ValueError("Source model missing from canonical registry")
    if not source.is_file() or not metadata.is_file():
        raise FileNotFoundError("Both downloaded source Release assets required")
    audit = verify_local(index, canonical, SOURCE_ID, source, metadata, check_load=True)
    if not (audit["weight_bytes_sha256_verified"]
            and audit["metadata_bytes_sha256_verified"] and audit["sb3_load_checked"]):
        raise ValueError("Failed Release data and CPU load gates")
    original = json.loads(metadata.read_text(encoding="utf-8"))
    if original["total_timesteps"] != parent["training_steps"]:
        raise ValueError("Source step counter mismatch")
    engine = verify_engine()
    if original["engine"] != engine:
        raise ValueError("Source engine mismatch")
    import torch
    torch.set_num_threads(2)
    trained_meta = train_run(steps=steps, seed=seed, model_out=dest, resume=source)
    new_sha = digest(dest)
    with zipfile.ZipFile(dest) as archive:
        names = set(archive.namelist())
        if not {"data", "policy.pth", "policy.optimizer.pth"}.issubset(names):
            raise ValueError("New model archive missing policy/optimizer")
        if archive.testzip() is not None:
            raise ValueError("New model archive has failed CRC")
    if trained_meta["engine"] != engine:
        raise ValueError("Resumed model environment drift")
    result = lineage_record(SOURCE_ID, parent["training_steps"],
                            parent["checkpoint_sha256"],
                            trained_meta["total_timesteps"], new_sha, steps)
    result["engine"] = engine
    result["training_seed"] = seed
    result["source_release_url"] = parent["release_url"]
    result["model_path"] = str(dest)
    result["metadata_path"] = str(dest.with_suffix(".metadata.json"))
    result["source_asset_bytes_verified"] = True
    result["parent_cpu_load_verified"] = True
    result["resumed_optimizer_checkpoint_present"] = True
    lineage.parent.mkdir(parents=True, exist_ok=True)
    lineage.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--lineage", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=128)
    parser.add_argument("--seed", type=int, default=92361)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--asset-index", type=Path,
                        default=Path("models/release_asset_digests.json"))
    args = parser.parse_args()
    print(json.dumps(smoke(args.source, args.out, args.lineage, args.steps,
                           args.seed, args.registry, args.asset_index)))


if __name__ == "__main__":
    main()
