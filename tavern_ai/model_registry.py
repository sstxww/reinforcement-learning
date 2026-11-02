"""Strict ZIP/archive preflight for the canonical main-branch model registry.

This complements tavern_ai.registry_integrity without creating a second registry.
No weight deserialization, training, match or Champion promotion is implied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .contract import (
    ACTIONS, CARDS, ENGINE_HASH, FEATURES, CATALOG_SHA256,
    RULESET_ID, PATCH_SHA256, UPSTREAM_COMMIT,
)

_REPO = "sstxww/reinforcement-learning"
_RELEASE_PREFIX = f"https://github.com/{_REPO}/releases/tag/"
_REQUIRED_ZIP_MEMBERS = {"data", "policy.pth", "policy.optimizer.pth"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_registry(path: Path) -> dict:
    """Validate the existing 4-model registry, never alter its Champion or provenance."""
    registry = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(registry, dict) or registry.get("schema") != 1:
        raise ValueError("Unsupported model registry schema")
    if registry.get("repository") != _REPO:
        raise ValueError("Repository mismatch")
    engine = registry.get("engine")
    required = {
        "version": "1.1.0", "source_hash": ENGINE_HASH,
        "float_features": FEATURES, "card_slots": CARDS,
        "action_count": ACTIONS,
    }
    if not isinstance(engine, dict) or any(engine.get(k) != v for k, v in required.items()):
        raise ValueError("Pinned engine/action/observation mismatch")
    if registry.get("champion") is not None or registry.get("best") is not None:
        raise ValueError("No independently established Champion; refusing promotion")
    entries = registry.get("candidates")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Missing canonical candidate records")
    ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Invalid candidate record")
        model_id = entry.get("id")
        if not isinstance(model_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", model_id):
            raise ValueError("Invalid model ID")
        if model_id in ids:
            raise ValueError("Duplicate model ID")
        ids.add(model_id)
        if entry.get("role") != "candidate_unpromoted":
            raise ValueError(f"Unverified promotion: {model_id}")
        sha = entry.get("checkpoint_sha256")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise ValueError(f"Invalid checkpoint SHA256: {model_id}")
        if entry.get("release_url") != _RELEASE_PREFIX + model_id:
            raise ValueError(f"Untrusted release URL: {model_id}")
        if type(entry.get("training_steps")) is not int or entry["training_steps"] <= 0:
            raise ValueError(f"Invalid training step count: {model_id}")
    latest = registry.get("latest")
    if not isinstance(latest, dict) or latest.get("id") not in ids:
        raise ValueError("Latest must refer to an indexed model")
    current = next(e for e in entries if e["id"] == latest["id"])
    if any([
        latest.get("checkpoint_sha256") != current["checkpoint_sha256"],
        latest.get("training_steps") != current["training_steps"],
        latest.get("release") != current["release_url"],
        latest.get("promoted_to_best") is not False,
    ]):
        raise ValueError("Latest/checkpoint inconsistent")
    return registry


def verify_archive(entry: dict, checkpoint: Path, metadata: Path) -> dict:
    """Check hash, schema 1/2 metadata, optimizer ZIP member and CRC without loading code."""
    if not checkpoint.is_file() or not metadata.is_file():
        raise FileNotFoundError("Both model.zip and model.metadata.json are required")
    actual_sha = sha256_file(checkpoint)
    if actual_sha != entry["checkpoint_sha256"]:
        raise ValueError("Checkpoint SHA256 mismatch; refusing restore")
    recorded = json.loads(metadata.read_text(encoding="utf-8"))
    if recorded.get("schema") not in (1, 2) or recorded.get("algorithm") != "MaskablePPO":
        raise ValueError("Unsupported training metadata")
    engine = recorded.get("engine")
    expected = {
        "version": "1.1.0", "source_hash": ENGINE_HASH,
        "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
    }
    if not isinstance(engine, dict) or any(engine.get(key) != value for key, value in expected.items()):
        raise ValueError("Engine, observation, card-vocabulary or action-space mismatch")
    if recorded["schema"] == 2:
        compatibility = {
            "engine": engine, "catalog_sha256": CATALOG_SHA256,
            "ruleset_id": RULESET_ID, "patch_sha256": PATCH_SHA256,
            "upstream_commit": UPSTREAM_COMMIT,
        }
        if recorded.get("compatibility") != compatibility:
            raise ValueError("Schema 2 catalog/ruleset/patch/upstream compatibility mismatch")
        if recorded.get("checkpoint_sha256") != actual_sha:
            raise ValueError("Embedded checkpoint SHA256 mismatch")
    if recorded.get("total_timesteps") != entry["training_steps"]:
        raise ValueError("Training steps conflict with canonical registry")
    try:
        with zipfile.ZipFile(checkpoint, "r") as archive:
            members = set(archive.namelist())
            if not _REQUIRED_ZIP_MEMBERS.issubset(members):
                raise ValueError("Missing PPO policy and optimizer state")
            if archive.testzip() is not None:
                raise ValueError("Corrupt checkpoint ZIP entry")
    except zipfile.BadZipFile as error:
        raise ValueError("Corrupt checkpoint ZIP") from error
    return {
        "model_id": entry["id"], "sha256": actual_sha,
        "total_timesteps": recorded["total_timesteps"],
        "optimizer_member_present": True,
        "status": "integrity_preflight_passed",
        "load_or_resume_verified_by_this_preflight": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--model-id")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()
    registry = read_registry(args.registry)
    if not args.model_id:
        print(json.dumps({
            "latest": registry["latest"]["id"],
            "models": [{"id": e["id"], "role": e["role"]}
                       for e in registry["candidates"]],
            "champion": None,
            "archive_bytes_verified_by_this_run": False,
        }, indent=2))
        return
    entry = next((e for e in registry["candidates"] if e["id"] == args.model_id), None)
    if entry is None:
        parser.error("Unknown model ID")
    if args.checkpoint is None or args.metadata is None:
        parser.error("--checkpoint and --metadata are required for archive integrity checks")
    print(json.dumps(verify_archive(entry, args.checkpoint, args.metadata), indent=2))


if __name__ == "__main__":
    main()
