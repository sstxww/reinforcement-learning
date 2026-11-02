"""Fail-closed metadata and archive preflight for historical PPO Releases.

This checks bytes and declared provenance, NOT executable model loading,
optimizer restoration, gameplay completion, or competitive promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .contract import ENGINE_HASH, FEATURES, CARDS, ACTIONS

_SHA256 = re.compile(r"^[a-f0-9]{64}$")


def load_registry(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != 1:
        raise ValueError("Unsupported registry schema")
    engine = data.get("engine", {})
    expected = ("1.1.0", ENGINE_HASH, FEATURES, CARDS, ACTIONS)
    actual = (engine.get("version"), engine.get("source_hash"),
              engine.get("float_features"), engine.get("card_slots"),
              engine.get("action_count"))
    if actual != expected:
        raise ValueError("Registry engine or observation contract mismatch")
    rows = data.get("candidates")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Missing model candidates")
    ids = set()
    for row in rows:
        ident, digest = row.get("id"), row.get("checkpoint_sha256")
        if not isinstance(ident, str) or not ident or ident in ids:
            raise ValueError("Duplicate or invalid model ID")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ValueError("Missing SHA256 for model " + ident)
        if type(row.get("training_steps")) is not int or row["training_steps"] <= 0:
            raise ValueError("Invalid training step count for " + ident)
        if row.get("promoted_to_best") is True:
            raise ValueError("Unreviewed model promotion in historical registry")
        ids.add(ident)
    latest = data.get("latest")
    if latest is not None and (
        latest.get("id") not in ids
        or latest.get("checkpoint_sha256") != next(
            r["checkpoint_sha256"] for r in rows if r["id"] == latest["id"]
        )
    ):
        raise ValueError("Latest pointer is not an indexed immutable candidate")
    if data.get("best") is not None:
        raise ValueError("No reviewed Champion is established by these records")
    return data


def verify_release_bytes(registry: dict, model_id: str, model: Path,
                         metadata: Path) -> dict:
    """Verify downloaded files without implicitly trusting their filenames."""
    matches = [r for r in registry["candidates"] if r["id"] == model_id]
    if len(matches) != 1:
        raise ValueError("Unknown model ID")
    row = matches[0]
    digest = hashlib.file_digest(model.open("rb"), "sha256").hexdigest()
    if digest != row["checkpoint_sha256"]:
        raise ValueError("Downloaded checkpoint SHA256 mismatch")
    if not zipfile.is_zipfile(model):
        raise ValueError("Checkpoint is not a valid ZIP container")
    with zipfile.ZipFile(model) as archive:
        if archive.testzip() is not None:
            raise ValueError("Checkpoint ZIP CRC failure")
    meta = json.loads(metadata.read_text(encoding="utf-8"))
    eng = meta.get("engine", {})
    if (eng.get("version"), eng.get("source_hash")) != ("1.1.0", ENGINE_HASH):
        raise ValueError("Checkpoint metadata engine mismatch")
    if meta.get("checkpoint_sha256") not in (None, digest):
        raise ValueError("Metadata checkpoint SHA256 mismatch")
    if meta.get("total_timesteps") != row["training_steps"]:
        raise ValueError("Model training steps do not match registry")
    return {
        "model_id": model_id, "sha256": digest,
        "integrity_verified": True, "metadata_compatible": True,
        "model_load_verified": False, "optimizer_resume_verified": False,
        "full_game_verified_by_this_check": False,
        "promoted_to_champion": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    p.add_argument("--model-id")
    p.add_argument("--model", type=Path)
    p.add_argument("--metadata", type=Path)
    a = p.parse_args()
    registry = load_registry(a.registry)
    if any(x is not None for x in (a.model_id, a.model, a.metadata)):
        if not all(x is not None for x in (a.model_id, a.model, a.metadata)):
            p.error("--model-id, --model and --metadata must be passed together")
        outcome = verify_release_bytes(registry, a.model_id, a.model, a.metadata)
    else:
        outcome = {
            "registry_valid": True,
            "indexed_candidates": len(registry["candidates"]),
            "champion": None,
            "download_or_resume_verified_by_this_check": False,
        }
    print(json.dumps(outcome, ensure_ascii=False))


if __name__ == "__main__":
    main()
