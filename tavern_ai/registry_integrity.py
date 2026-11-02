"""Fail-closed checks for the tracked unpromoted TavernGym model registry.

This module never downloads, loads, resumes, promotes or changes model weights.
A registry SHA is a claim to verify against actual downloaded bytes, not proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

RELEASE_PREFIX = "https://github.com/sstxww/reinforcement-learning/releases/tag/"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SOURCE_HASH = "6d8712c93022ba11"


def validate_registry(data: dict) -> dict:
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError("Unsupported registry schema")
    if data.get("repository") != "sstxww/reinforcement-learning":
        raise ValueError("Unexpected repository")
    engine = data.get("engine")
    if not isinstance(engine, dict) or any((
        engine.get("version") != "1.1.0",
        engine.get("source_hash") != SOURCE_HASH,
        engine.get("float_features") != 4017,
        engine.get("card_slots") != 447,
        engine.get("action_count") != 245,
    )):
        raise ValueError("Incompatible TavernGym observation/action contract")
    if data.get("best") is not None or data.get("champion") is not None:
        raise ValueError("This registry has no verified champion; reject promotion")
    rows = data.get("candidates")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Missing candidate models")
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Malformed candidate")
        model_id = row.get("id")
        if not isinstance(model_id, str) or not model_id or model_id in seen:
            raise ValueError("Missing or duplicate model ID")
        seen.add(model_id)
        if not SHA256.fullmatch(str(row.get("checkpoint_sha256", ""))):
            raise ValueError("Invalid candidate checkpoint SHA256")
        if type(row.get("training_steps")) is not int or row["training_steps"] <= 0:
            raise ValueError("Invalid cumulative training steps")
        if row.get("role") != "candidate_unpromoted":
            raise ValueError("Unreviewed model promotion")
        if row.get("release_url") != RELEASE_PREFIX + model_id:
            raise ValueError("Candidate release URL/ID mismatch")
    latest = data.get("latest")
    if not isinstance(latest, dict) or latest.get("id") not in seen:
        raise ValueError("Latest must refer to a registered candidate")
    row = next(row for row in rows if row["id"] == latest["id"])
    if (latest.get("checkpoint_sha256") != row["checkpoint_sha256"]
            or latest.get("training_steps") != row["training_steps"]
            or latest.get("release") != row["release_url"]
            or latest.get("release_tag") != row["id"]
            or latest.get("model_asset") != "model.zip"
            or latest.get("metadata_asset") != "model.metadata.json"
            or latest.get("promoted_to_best") is not False):
        raise ValueError("Latest provenance mismatch or unsafe promotion")
    return {"schema": 1, "candidates": len(rows), "champion": None,
            "latest_id": latest["id"], "latest_steps": latest["training_steps"],
            "checkpoint_bytes_checked": False, "release_resume_checked": False}


def verify_checkpoint(path: Path, expected_sha256: str) -> str:
    if not SHA256.fullmatch(expected_sha256):
        raise ValueError("Invalid expected SHA256")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != expected_sha256:
        raise ValueError("Checkpoint SHA256 mismatch; do not load or resume")
    return actual


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--checkpoint", type=Path, help="Downloaded real model.zip, never inferred")
    parser.add_argument("--model-id", type=str, help="Required for checkpoint verification")
    args = parser.parse_args()
    data = json.loads(args.registry.read_text(encoding="utf-8"))
    summary = validate_registry(data)
    if args.checkpoint is not None:
        if not args.model_id:
            parser.error("--checkpoint requires --model-id")
        row = next((r for r in data["candidates"] if r["id"] == args.model_id), None)
        if row is None:
            parser.error("Unknown model ID")
        summary["checkpoint_sha256_verified"] = verify_checkpoint(
            args.checkpoint, row["checkpoint_sha256"])
        summary["checkpoint_bytes_checked"] = True
    elif args.model_id:
        parser.error("--model-id requires --checkpoint")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
