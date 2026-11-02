"""Read-only, fail-closed registry and integrity preflight for archived PPO checkpoints.

This tool does not mark a model as restored/strong solely because its Release exists.
It never deserializes an untrusted PyTorch checkpoint: actual load/resume/inference
must be separately tested in a trusted pinned engine after this preflight.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .contract import (ACTIONS, CARDS, ENGINE_HASH, FEATURES, CATALOG_SHA256,
                       RULESET_ID, PATCH_SHA256, UPSTREAM_COMMIT)

_STATUSES = {"Unverified", "Challenger", "Latest", "Population", "Rejected", "Champion"}
_REQUIRED_ZIP_MEMBERS = {"data", "policy.pth", "policy.optimizer.pth"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_registry(path: Path) -> dict:
    registry = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(registry, dict) or registry.get("schema") != 1:
        raise ValueError("Unsupported model registry schema")
    entries = registry.get("models")
    if not isinstance(entries, list):
        raise ValueError("Model registry requires a models list")
    champion_id = registry.get("champion_id")
    if champion_id is not None and not isinstance(champion_id, str):
        raise ValueError("Invalid Champion reference")
    ids: set[str] = set()
    champions: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Invalid model record")
        model_id = entry.get("model_id")
        if not isinstance(model_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", model_id):
            raise ValueError("Invalid model ID")
        if model_id in ids:
            raise ValueError("Duplicate model ID")
        ids.add(model_id)
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"Invalid checkpoint SHA256: {model_id}")
        if entry.get("status") not in _STATUSES:
            raise ValueError(f"Unknown model status: {model_id}")
        if entry.get("engine_source_hash") != ENGINE_HASH:
            raise ValueError(f"Unpinned engine for {model_id}")
        if not isinstance(entry.get("release_url"), str) or not entry["release_url"].startswith(
            "https://github.com/sstxww/reinforcement-learning/releases/tag/"
        ):
            raise ValueError(f"Missing durable Release URL: {model_id}")
        steps = entry.get("training_steps")
        if steps is not None and (type(steps) is not int or steps < 0):
            raise ValueError(f"Invalid training step count: {model_id}")
        for flag in ("load_verified", "resume_verified", "full_game_verified", "paired_eval_verified"):
            if type(entry.get(flag)) is not bool:
                raise ValueError(f"Missing explicit {flag}: {model_id}")
        if entry["status"] == "Champion":
            champions.append(model_id)
            if not all(entry[flag] for flag in (
                "load_verified", "resume_verified", "full_game_verified", "paired_eval_verified"
            )):
                raise ValueError(f"Champion lacks verification gates: {model_id}")
    if len(champions) > 1 or (champions[0] if champions else None) != champion_id:
        raise ValueError("Champion pointer and verified status disagree")
    return registry


def verify_archive(entry: dict, checkpoint: Path, metadata: Path) -> dict:
    """Check declared SHA, compatibility metadata, archive contents and CRC, without loading code."""
    if not checkpoint.is_file() or not metadata.is_file():
        raise FileNotFoundError("Both checkpoint ZIP and metadata JSON are required")
    actual_sha = sha256_file(checkpoint)
    if actual_sha != entry["sha256"]:
        raise ValueError("Checkpoint SHA256 mismatch; refusing to restore")
    recorded = json.loads(metadata.read_text(encoding="utf-8"))
    if recorded.get("schema") not in (1, 2) or recorded.get("algorithm") != "MaskablePPO":
        raise ValueError("Unsupported training metadata")
    engine = recorded.get("engine")
    expected = {"version": "1.1.0", "source_hash": ENGINE_HASH,
                "features": FEATURES, "cards": CARDS, "actions": ACTIONS}
    if not isinstance(engine, dict) or any(engine.get(key) != value for key, value in expected.items()):
        raise ValueError("Engine, observation, card vocabulary or action space mismatch")
    if recorded["schema"] == 2:
        compatibility = recorded.get("compatibility")
        expected_compatibility = {
            "engine": engine,
            "catalog_sha256": CATALOG_SHA256,
            "ruleset_id": RULESET_ID,
            "patch_sha256": PATCH_SHA256,
            "upstream_commit": UPSTREAM_COMMIT,
        }
        if compatibility != expected_compatibility:
            raise ValueError("Schema 2 catalog/ruleset/patch/upstream compatibility mismatch")
        if recorded.get("checkpoint_sha256") != actual_sha:
            raise ValueError("Embedded checkpoint SHA256 mismatch")
    if entry.get("training_steps") is not None and recorded.get("total_timesteps") != entry["training_steps"]:
        raise ValueError("Training step count conflicts with registry")
    try:
        with zipfile.ZipFile(checkpoint, "r") as archive:
            members = set(archive.namelist())
            if not _REQUIRED_ZIP_MEMBERS.issubset(members):
                raise ValueError("Missing PPO policy and optimizer state")
            if archive.testzip() is not None:
                raise ValueError("Corrupt checkpoint ZIP entry")
    except zipfile.BadZipFile as error:
        raise ValueError("Corrupt checkpoint ZIP") from error
    return {"model_id": entry["model_id"], "sha256": actual_sha,
            "total_timesteps": recorded["total_timesteps"],
            "optimizer_member_present": True, "status": "integrity_preflight_passed",
            "load_or_resume_verified": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--model-id")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()
    registry = read_registry(args.registry)
    if not args.model_id:
        print(json.dumps({"models": [
            {"model_id": e["model_id"], "status": e["status"],
             "load_verified": e["load_verified"], "resume_verified": e["resume_verified"]}
            for e in registry["models"]], "champion_id": registry["champion_id"]}, indent=2))
        return
    entry = next((e for e in registry["models"] if e["model_id"] == args.model_id), None)
    if entry is None:
        parser.error("Unknown model ID")
    if args.checkpoint is None or args.metadata is None:
        parser.error("--checkpoint and --metadata are required to verify a model")
    print(json.dumps(verify_archive(entry, args.checkpoint, args.metadata), indent=2))


if __name__ == "__main__":
    main()
