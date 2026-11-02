"""Fail-closed local verification for versioned TavernGym Release checkpoints.

This gate is deliberately separate from the currently shared trainer. It does not
make a model Champion or claim a checkpoint can resume until actually tested.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from tavern_ai.contract import (ACTIONS, CARDS, FEATURES, ENGINE_HASH,
    CATALOG_SHA256, PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT)

REPOSITORY = "sstxww/reinforcement-learning"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def read_registry(path: Path) -> dict:
    p = json.loads(path.read_text(encoding="utf-8"))
    if p.get("schema") != 1 or p.get("repository") != REPOSITORY:
        raise ValueError("Unsupported checkpoint registry")
    expected = {"version": "1.1.0", "source_hash": ENGINE_HASH,
                "features": FEATURES, "cards": CARDS, "actions": ACTIONS}
    if p.get("engine") != expected:
        raise ValueError("Registry engine contract mismatch")
    if p.get("champion") is not None:
        raise ValueError("No independent evidence for Champion promotion")
    seen = set()
    for record in p.get("checkpoints", []):
        tag = record.get("release_tag")
        model_hash = record.get("sha256")
        if (not isinstance(tag, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", tag)
                or record.get("id") != tag or tag in seen
                or not isinstance(model_hash, str) or not HEX64.fullmatch(model_hash)
                or type(record.get("steps")) is not int or record["steps"] < 128
                or record.get("role") != "challenger"
                or record.get("model_asset") != "model.zip"
                or record.get("metadata_asset") != "model.metadata.json"):
            raise ValueError("Invalid, duplicated or untrusted checkpoint record")
        seen.add(tag)
    if not seen or p.get("latest_candidate") not in seen:
        raise ValueError("Invalid latest candidate")
    for record in p["checkpoints"]:
        if record.get("parent") is not None and record["parent"] not in seen:
            raise ValueError("Unresolvable model parent")
    return p


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def verify_checkpoint(model: Path, metadata: Path, registry: dict,
                      candidate: str) -> dict:
    items = {r["id"]: r for r in registry["checkpoints"]}
    if candidate not in items:
        raise ValueError("Unknown model version")
    record = items[candidate]
    actual = hash_file(model)
    if actual != record["sha256"]:
        raise ValueError("Release checkpoint SHA256 mismatch")
    meta = json.loads(metadata.read_text(encoding="utf-8"))
    engine = meta.get("engine")
    if not isinstance(engine, dict):
        raise ValueError("Missing model engine metadata")
    for key, value in (("version", "1.1.0"), ("source_hash", ENGINE_HASH),
                       ("features", FEATURES), ("cards", CARDS), ("actions", ACTIONS)):
        if engine.get(key) != value:
            raise ValueError(f"Model engine mismatch: {key}")
    if type(meta.get("total_timesteps")) is not int or meta["total_timesteps"] != record["steps"]:
        raise ValueError("Checkpoint training step lineage mismatch")
    if meta.get("checkpoint_sha256") not in (None, actual):
        raise ValueError("Embedded model SHA256 mismatch")
    compatibility = meta.get("compatibility")
    if compatibility is not None:
        expected = {"engine": engine, "catalog_sha256": CATALOG_SHA256,
                    "ruleset_id": RULESET_ID, "patch_sha256": PATCH_SHA256,
                    "upstream_commit": UPSTREAM_COMMIT}
        if compatibility != expected:
            raise ValueError("Full model compatibility metadata mismatch")
    return {"candidate": candidate, "model_sha256": actual,
            "verified_steps": meta["total_timesteps"],
            "engine_version": engine["version"],
            "source_hash": engine["source_hash"],
            "byte_integrity_verified": True, "model_loading_verified": False,
            "resume_training_verified": False}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    p.add_argument("--candidate", default="v2-learning-41413557445")
    p.add_argument("--model", type=Path)
    p.add_argument("--metadata", type=Path)
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    registry = read_registry(a.registry)
    if (a.model is None) != (a.metadata is None):
        p.error("--model and --metadata must be provided together")
    summary = {"registry_valid": True, "latest_candidate": registry["latest_candidate"]}
    if a.model is not None:
        summary.update(verify_checkpoint(a.model, a.metadata, registry, a.candidate))
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
