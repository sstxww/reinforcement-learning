"""Strict, non-promoting V5 release-checkpoint audit for the pinned TavernGym contract.

Audits an immutable release record, bytes, compatibility metadata and optionally
loads the actual PPO policy and its optimizer. This is NOT a Champion selector.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_ENGINE_KEYS = ("version", "source_hash", "features", "cards", "actions")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_release(registry_path: Path, model_id: str, model_path: Path,
                  metadata_path: Path, runtime: bool = False) -> dict:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("schema") != 1 or registry.get("champion") is not None:
        raise ValueError("Registry schema invalid or unverified Champion present")
    entries = registry.get("candidates")
    if not isinstance(entries, list) or sum(x.get("id") == model_id for x in entries) != 1:
        raise ValueError("Expected exactly one registered candidate ID")
    entry = next(x for x in entries if x["id"] == model_id)
    if entry.get("role") != "challenger" or entry.get("promotion_verified") is not False:
        raise ValueError("Unexpected candidate role or promotion status")
    if not model_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError("Both model archive and metadata must exist")
    actual_sha = sha256_file(model_path)
    expected_sha = entry.get("sha256")
    if actual_sha != expected_sha:
        raise ValueError(f"Checkpoint SHA256 mismatch: expected {expected_sha}, got {actual_sha}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("schema") != 1 or metadata.get("algorithm") != "MaskablePPO":
        raise ValueError("Incompatible checkpoint metadata schema/algorithm")
    if type(metadata.get("total_timesteps")) is not int or metadata["total_timesteps"] != entry["training_steps"]:
        raise ValueError("Training step count differs from registry")
    saved_engine = metadata.get("engine")
    expected_engine = entry.get("engine")
    if not isinstance(saved_engine, dict) or not isinstance(expected_engine, dict):
        raise ValueError("Engine fingerprint missing")
    for key in REQUIRED_ENGINE_KEYS:
        if saved_engine.get(key) != expected_engine.get(key):
            raise ValueError(f"Checkpoint engine mismatch in {key}")
    optimizer_state = "not_tested"
    if runtime:
        from .contract import verify_engine
        current_engine = verify_engine()
        for key in REQUIRED_ENGINE_KEYS:
            if current_engine.get(key) != expected_engine[key]:
                raise ValueError(f"Runtime engine mismatch in {key}")
        from sb3_contrib import MaskablePPO
        model = MaskablePPO.load(str(model_path), device="cpu")
        if int(model.num_timesteps) != entry["training_steps"]:
            raise ValueError("Loaded PPO timestep counter differs")
        if model.action_space.n != expected_engine["actions"]:
            raise ValueError("Loaded PPO action space differs")
        if tuple(model.observation_space["features"].shape) != (expected_engine["features"],):
            raise ValueError("Loaded PPO numerical observation differs")
        if tuple(model.observation_space["cards"].shape) != (expected_engine["cards"],):
            raise ValueError("Loaded PPO card observation differs")
        optimizer = getattr(model.policy, "optimizer", None)
        state = optimizer.state_dict().get("state") if optimizer is not None else None
        if not state:
            raise ValueError("Loaded checkpoint has no nonempty optimizer state for genuine continuation")
        optimizer_state = "loaded_nonempty"
    return {
        "schema": 1, "checked_at": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id, "role": "challenger", "sha256": actual_sha,
        "release_tag": entry["release_tag"], "source_commit": entry["source_commit"],
        "total_timesteps": metadata["total_timesteps"], "engine": expected_engine,
        "optimizer_state": optimizer_state,
        "status": "load_and_optimizer_verified" if runtime else "file_and_metadata_verified",
        "eligible_for_champion": False,
        "notes": "Recovery verification does not establish match strength or safe model promotion.",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--registry", type=Path, required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--runtime", action="store_true")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = audit_release(args.registry, args.id, args.model, args.metadata, args.runtime)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
