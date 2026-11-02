"""Strict verification gate for versioned candidate Releases (not a promoter).

Accepts the already merged main model registry, including its rich V1 schema.
Does not change a model, grant Champion status, or infer strength from a smoke game.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from tavern_ai.contract import (
    ACTIONS, CARDS, FEATURES, ENGINE_HASH, CATALOG_SHA256,
    PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT,
)

REPOSITORY = "sstxww/reinforcement-learning"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
TAG = re.compile(r"[a-zA-Z0-9._-]+\Z")


def _candidates(registry: dict) -> list[dict]:
    records = registry.get("candidates", registry.get("checkpoints"))
    if not isinstance(records, list) or not records:
        raise ValueError("No versioned candidates registered")
    return records


def _normalized(record: dict) -> dict:
    if not isinstance(record, dict):
        raise ValueError("Invalid checkpoint record")
    version = record.get("id")
    digest = record.get("checkpoint_sha256", record.get("sha256"))
    steps = record.get("training_steps", record.get("steps"))
    if (
        not isinstance(version, str) or not TAG.fullmatch(version)
        or not isinstance(digest, str) or not HEX64.fullmatch(digest)
        or type(steps) is not int or steps < 128
    ):
        raise ValueError("Invalid checkpoint version, steps or SHA256")
    return {"id": version, "sha256": digest, "steps": steps}


def read_registry(path: Path) -> dict:
    registry = json.loads(path.read_text(encoding="utf-8"))
    if registry.get("schema") != 1 or registry.get("repository") != REPOSITORY:
        raise ValueError("Unknown registry contract")
    engine = registry.get("engine") or {}
    actual = (
        engine.get("version"), engine.get("source_hash"),
        engine.get("float_features", engine.get("features")),
        engine.get("card_slots", engine.get("cards")),
        engine.get("action_count", engine.get("actions")),
    )
    expected = ("1.1.0", ENGINE_HASH, FEATURES, CARDS, ACTIONS)
    if actual != expected:
        raise ValueError("Registry TavernGym contract mismatch")
    if registry.get("champion") is not None or registry.get("best") is not None:
        raise ValueError("Champion requires separate independent promotion proof")
    seen = set()
    for record in _candidates(registry):
        checkpoint = _normalized(record)
        if checkpoint["id"] in seen:
            raise ValueError("Duplicate candidate checkpoint version")
        seen.add(checkpoint["id"])
    latest = registry.get("latest_candidate") or (registry.get("latest") or {}).get("id")
    if latest not in seen:
        raise ValueError("Latest candidate not present in versioned candidates")
    return registry


def hash_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as file:
        while block := file.read(1024 * 1024):
            sha.update(block)
    return sha.hexdigest()


def verify_checkpoint(model_path: Path, metadata_path: Path, registry: dict, candidate_id: str) -> dict:
    selected = next(
        (_normalized(item) for item in _candidates(registry) if item.get("id") == candidate_id),
        None,
    )
    if selected is None:
        raise ValueError("Unknown candidate checkpoint")
    actual_sha = hash_file(model_path)
    if selected["sha256"] != actual_sha:
        raise ValueError("Release model SHA256 mismatch")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    engine = metadata.get("engine")
    if not isinstance(engine, dict):
        raise ValueError("Checkpoint engine metadata missing")
    expected = {
        "version": "1.1.0", "source_hash": ENGINE_HASH,
        "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
    }
    for key, expected_value in expected.items():
        if engine.get(key) != expected_value:
            raise ValueError("Checkpoint TavernGym engine mismatch: " + key)
    if type(metadata.get("total_timesteps")) is not int or metadata["total_timesteps"] != selected["steps"]:
        raise ValueError("Model checkpoint total_timesteps lineage mismatch")
    if metadata.get("checkpoint_sha256") not in (None, actual_sha):
        raise ValueError("Model metadata-embedded SHA256 mismatch")
    if metadata.get("compatibility") is not None:
        compatibility = {
            "engine": engine, "catalog_sha256": CATALOG_SHA256, "ruleset_id": RULESET_ID,
            "patch_sha256": PATCH_SHA256, "upstream_commit": UPSTREAM_COMMIT,
        }
        if metadata["compatibility"] != compatibility:
            raise ValueError("Model metadata compatibility mismatch")
    return {
        "candidate_id": candidate_id, "model_sha256": actual_sha,
        "verified_timesteps": selected["steps"], "release_bytes_verified": True,
        "weights_loaded_by_python": False, "resumed_training_executed": False,
        "promotion": "NOT_ELIGIBLE_BY_CHECKSUM_ONLY",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--candidate", default="v2-learning-41413557445")
    parser.add_argument("--model", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if (args.model is None) != (args.metadata is None):
        parser.error("model and metadata must both be supplied")
    registry = read_registry(args.registry)
    result = {"registry_verified": True,
              "latest": registry.get("latest_candidate") or registry["latest"]["id"]}
    if args.model:
        result.update(verify_checkpoint(args.model, args.metadata, registry, args.candidate))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
