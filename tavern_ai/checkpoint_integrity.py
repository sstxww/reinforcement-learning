"""Fail-closed checks for resumable PPO checkpoint bytes and metadata.

This module intentionally does not import torch or TavernGym at import time.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

_SHA = re.compile(r"[0-9a-f]{64}\Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def metadata_path(checkpoint: Path) -> Path:
    return checkpoint.with_suffix(".metadata.json")


def pinned_compatibility(engine: dict) -> dict:
    """The stronger schema-2 fingerprint published by the V1/V2 learning work."""
    from .contract import CATALOG_SHA256, RULESET_ID, PATCH_SHA256, UPSTREAM_COMMIT
    return {"engine": engine, "catalog_sha256": CATALOG_SHA256,
            "ruleset_id": RULESET_ID, "patch_sha256": PATCH_SHA256,
            "upstream_commit": UPSTREAM_COMMIT}


def verify_checkpoint(checkpoint: Path, expected_engine: dict | None = None,
                      expected_sha256: str | None = None) -> dict:
    """Reject missing, mismatched or corrupted checkpoints *before* PPO.load()."""
    checkpoint = Path(checkpoint)
    if not checkpoint.is_file():
        raise FileNotFoundError(checkpoint)
    companion = metadata_path(checkpoint)
    if not companion.is_file():
        raise ValueError(f"Missing checkpoint metadata: {companion}")
    try:
        meta = json.loads(companion.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise ValueError("Invalid checkpoint metadata JSON") from exc
    if not isinstance(meta, dict) or type(meta.get("schema")) is not int or meta["schema"] not in (1, 2):
        raise ValueError("Unsupported checkpoint metadata schema")
    if meta.get("algorithm") != "MaskablePPO":
        raise ValueError("Unexpected model algorithm")
    if type(meta.get("total_timesteps")) is not int or meta["total_timesteps"] < 1:
        raise ValueError("Invalid cumulative training steps")
    if not isinstance(meta.get("engine"), dict):
        raise ValueError("Missing engine fingerprint")
    if expected_engine is not None and meta["engine"] != expected_engine:
        raise ValueError("Checkpoint engine or card vocabulary mismatch")
    if meta["schema"] == 2 and meta.get("compatibility") != pinned_compatibility(meta["engine"]):
        raise ValueError("Checkpoint source catalog, ruleset or engine compatibility mismatch")
    digest = meta.get("checkpoint_sha256")
    if not isinstance(digest, str) or not _SHA.fullmatch(digest):
        raise ValueError("Missing or invalid checkpoint SHA256; refuse unverified resume")
    actual = sha256_file(checkpoint)
    if not hmac.compare_digest(actual, digest):
        raise ValueError("Checkpoint SHA256 mismatch")
    if expected_sha256 is not None:
        if not _SHA.fullmatch(expected_sha256) or not hmac.compare_digest(actual, expected_sha256):
            raise ValueError("Checkpoint release digest mismatch")
    try:
        with zipfile.ZipFile(checkpoint) as archive:
            if archive.testzip() is not None:
                raise ValueError("Corrupt checkpoint ZIP member")
    except (zipfile.BadZipFile, OSError) as exc:
        raise ValueError("Invalid checkpoint ZIP") from exc
    return meta


def save_checkpoint(model, destination: Path, metadata: dict) -> dict:
    """Stage weights and companion metadata before switching the live files.

    A prior checkpoint is retained as *.previous.zip/.metadata.json on overwrite;
    the new pair is verified first and a failed save never replaces the old pair.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.suffix != ".zip":
        raise ValueError("Checkpoint destination must end in .zip")
    if not isinstance(metadata, dict) or metadata.get("engine") is None:
        raise ValueError("Engine metadata required")
    with tempfile.TemporaryDirectory(prefix=".checkpoint-", dir=destination.parent) as temp:
        staged = Path(temp) / destination.name
        model.save(str(staged))
        if not staged.is_file():
            raise ValueError("Model did not save a checkpoint")
        complete = dict(metadata, schema=metadata.get("schema", 1), checkpoint_sha256=sha256_file(staged))
        staged_meta = metadata_path(staged)
        staged_meta.write_text(json.dumps(complete, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        verify_checkpoint(staged, expected_engine=complete["engine"])
        current_meta = metadata_path(destination)
        if destination.exists() or current_meta.exists():
            if not destination.is_file() or not current_meta.is_file():
                raise ValueError("Refuse overwrite of incomplete checkpoint pair")
            # Old pairs without a digest are still preserved (not trusted for restore).
            backup = destination.with_name(destination.stem + ".previous.zip")
            backup_meta = metadata_path(backup)
            shutil.copy2(destination, backup)
            shutil.copy2(current_meta, backup_meta)
        # The staged pair is fully validated. On interrupted replacement, old bytes
        # remain in *.previous.zip and the mismatched live pair fails closed.
        os.replace(staged, destination)
        os.replace(staged_meta, current_meta)
        return complete


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify checkpoint bytes, metadata and engine")
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--check-engine", action="store_true")
    args = parser.parse_args()
    if args.check_engine:
        from .contract import verify_engine
        engine = verify_engine()
    else:
        engine = None
    meta = verify_checkpoint(args.checkpoint, engine, args.expected_sha256)
    print(json.dumps({"checkpoint": str(args.checkpoint), "sha256": meta["checkpoint_sha256"],
                      "total_timesteps": meta["total_timesteps"], "verified": True}))


if __name__ == "__main__":
    main()
