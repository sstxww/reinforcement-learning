"""Fail-closed integrity verification for the *main* release registry format.

Reads models/registry.json without rewriting the shared registry, downloading
from GitHub or claiming checkpoint compatibility from a ZIP alone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

EXPECTED_ENGINE = {
    "name": "TavernGym",
    "version": "1.1.0",
    "observation": "observe2",
    "float_features": 4017,
    "card_slots": 447,
    "action_count": 245,
    "source_hash": "6d8712c93022ba11",
}


def validate_registry(index: dict) -> dict[str, dict]:
    if not isinstance(index, dict) or index.get("schema") != 1:
        raise ValueError("Unsupported registry schema")
    if index.get("repository") != "sstxww/reinforcement-learning":
        raise ValueError("Wrong model registry repository")
    if index.get("engine") != EXPECTED_ENGINE:
        raise ValueError("Engine, catalog or observation contract mismatch")
    entries = index.get("candidates")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Missing model candidate records")
    by_id: dict[str, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Invalid model entry")
        model_id = entry.get("id")
        if not isinstance(model_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,120}", model_id):
            raise ValueError("Invalid model id")
        if model_id in by_id:
            raise ValueError("Duplicate model id")
        if entry.get("role") not in ("candidate_unpromoted", "rejected", "population", "champion"):
            raise ValueError("Invalid model role")
        if entry.get("release_url") != "https://github.com/sstxww/reinforcement-learning/releases/tag/" + model_id:
            raise ValueError("Release identity mismatch")
        if not isinstance(entry.get("checkpoint_sha256"), str) or re.fullmatch(r"[a-f0-9]{64}", entry["checkpoint_sha256"]) is None:
            raise ValueError("Missing/invalid checkpoint SHA256")
        if type(entry.get("training_steps")) is not int or entry["training_steps"] <= 0:
            raise ValueError("Invalid cumulative training step count")
        by_id[model_id] = entry
    for model_id, entry in by_id.items():
        parent = entry.get("source_release")
        if parent is not None:
            if parent not in by_id or parent == model_id:
                raise ValueError("Missing or self-referential parent checkpoint")
            if by_id[parent]["training_steps"] >= entry["training_steps"]:
                raise ValueError("Parent checkpoint not earlier than descendant")
            visited = {model_id}
            while parent:
                if parent in visited:
                    raise ValueError("Cyclic parent checkpoint provenance")
                visited.add(parent)
                parent = by_id[parent].get("source_release")
    latest = index.get("latest")
    if not isinstance(latest, dict) or latest.get("id") not in by_id:
        raise ValueError("Latest checkpoint missing from candidate index")
    current = by_id[latest["id"]]
    if (latest.get("release_tag") != latest["id"] or
        latest.get("checkpoint_sha256") != current["checkpoint_sha256"] or
        latest.get("training_steps") != current["training_steps"]):
        raise ValueError("Latest pointer mismatches indexed checkpoint")
    champion = index.get("champion")
    if champion is not None:
        if (champion not in by_id or by_id[champion]["role"] != "champion"
            or not index.get("champion_promotion_evidence")):
            raise ValueError("Champion cannot be claimed without verified promotion")
    if index.get("best") is not None:
        raise ValueError("Best may not be automatically promoted")
    if champion is None and any(e["role"] == "champion" for e in entries):
        raise ValueError("Champion record without promoted champion ID")
    return by_id


def load_registry(path: Path) -> tuple[dict, dict[str, dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, validate_registry(data)


def verify_asset(entry: dict, model_path: Path) -> dict:
    """Only checksum and archive structural integrity, not a policy-load claim."""
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    hash_state = hashlib.sha256()
    with model_path.open("rb") as fp:
        for block in iter(lambda: fp.read(1024 * 1024), b""):
            hash_state.update(block)
    digest = hash_state.hexdigest()
    if digest != entry["checkpoint_sha256"]:
        raise ValueError("Checkpoint SHA256 mismatch; refusing restore")
    if not zipfile.is_zipfile(model_path):
        raise ValueError("Invalid PPO checkpoint ZIP")
    with zipfile.ZipFile(model_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Corrupt PPO checkpoint ZIP member")
    return {"model_id": entry["id"], "sha256": digest,
            "bytes": model_path.stat().st_size,
            "integrity": "sha256_and_zip_ok",
            "load_and_optimizer_resume_verified_by_this_check": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--model-id")
    parser.add_argument("--asset", type=Path)
    args = parser.parse_args()
    registry, by_id = load_registry(args.registry)
    if (args.model_id is None) != (args.asset is None):
        parser.error("--model-id and --asset must be supplied together")
    if args.model_id:
        if args.model_id not in by_id:
            parser.error("Unknown model ID")
        print(json.dumps(verify_asset(by_id[args.model_id], args.asset), sort_keys=True))
    else:
        print(json.dumps({"validated": len(by_id), "latest": registry["latest"]["id"],
                          "champion": registry["champion"]}, sort_keys=True))


if __name__ == "__main__":
    main()
