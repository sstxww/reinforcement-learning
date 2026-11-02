"""Offline, fail-closed registry and SHA/ZIP validation for durable PPO releases.

This tool does not download files, infer a Champion, or imply the checkpoint
can actually resume training. Release-based load/resume needs a separate gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROLES = {"challenger", "population", "rejected", "champion"}
REQUIRED_ENGINE = {
    "name": "TavernGym",
    "version": "1.1.0",
    "observation": "observe2",
    "features": 4017,
    "cards": 447,
    "actions": 245,
    "source_hash": "6d8712c93022ba11",
}


def validate_registry(index: dict) -> dict[str, dict]:
    if not isinstance(index, dict) or index.get("schema") != 1:
        raise ValueError("Unsupported registry schema")
    if index.get("repository") != "sstxww/reinforcement-learning":
        raise ValueError("Unexpected repository")
    if index.get("engine") != REQUIRED_ENGINE:
        raise ValueError("Engine or observation contract mismatch")
    entries = index.get("models")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Empty registry")
    by_id: dict[str, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Invalid model entry")
        model_id = entry.get("id")
        if not isinstance(model_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,120}", model_id):
            raise ValueError("Invalid model id")
        if model_id in by_id:
            raise ValueError("Duplicate model id")
        if entry.get("status") not in ROLES:
            raise ValueError("Invalid model status")
        if entry.get("release_tag") != model_id or entry.get("asset") != "model.zip":
            raise ValueError("Release identity mismatch")
        if not isinstance(entry.get("sha256"), str) or re.fullmatch(r"[a-f0-9]{64}", entry["sha256"]) is None:
            raise ValueError("Missing/invalid checkpoint SHA256")
        if type(entry.get("steps")) is not int or entry["steps"] <= 0:
            raise ValueError("Invalid step count")
        if type(entry.get("source_pr")) is not int or entry["source_pr"] <= 0:
            raise ValueError("Missing source PR")
        if type(entry.get("release_resume_verified")) is not bool:
            raise ValueError("Missing release resume verification flag")
        full = entry.get("full_match")
        if full is not None:
            if (not isinstance(full, dict) or full.get("completed") is not True
                or type(full.get("seed")) is not int or type(full.get("rank")) is not int
                or not 1 <= full["rank"] <= 8):
                raise ValueError("Invalid full-match evidence")
        heldout = entry.get("heldout")
        if not isinstance(heldout, dict):
            raise ValueError("Missing heldout data")
        seeds, ranks = heldout.get("seeds"), heldout.get("ranks")
        if (not isinstance(seeds, list) or not isinstance(ranks, list)
            or not seeds or len(seeds) != len(ranks)
            or any(type(s) is not int or s < 0 for s in seeds)
            or any(type(r) is not int or r not in range(1, 9) for r in ranks)):
            raise ValueError("Invalid heldout seeds/ranks")
        by_id[model_id] = entry
    for model_id, entry in by_id.items():
        parent = entry.get("parent")
        if parent is not None:
            if parent not in by_id or parent == model_id:
                raise ValueError("Missing/self parent")
            if by_id[parent]["steps"] >= entry["steps"]:
                raise ValueError("Parent checkpoint is not earlier")
            visited = {model_id}
            while parent is not None:
                if parent in visited:
                    raise ValueError("Cyclic provenance")
                visited.add(parent)
                parent = by_id[parent].get("parent")
    latest, champion = index.get("latest"), index.get("champion")
    if latest not in by_id:
        raise ValueError("Latest is not an indexed checkpoint")
    if champion is not None:
        if champion not in by_id or by_id[champion]["status"] != "champion":
            raise ValueError("Champion must be explicitly validated and registered")
        if not index.get("champion_promotion_evidence"):
            raise ValueError("Missing champion promotion evidence")
    if champion is None and any(x["status"] == "champion" for x in entries):
        raise ValueError("Cannot advertise champion when champion ID is null")
    return by_id


def load_registry(path: Path) -> tuple[dict, dict[str, dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, validate_registry(data)


def verify_asset(entry: dict, model_path: Path) -> dict:
    """Validate a downloaded release asset without trusting its filename."""
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    h = hashlib.sha256()
    with model_path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            h.update(block)
    actual = h.hexdigest()
    if actual != entry["sha256"]:
        raise ValueError("Checkpoint SHA256 mismatch; refusing restore")
    if not zipfile.is_zipfile(model_path):
        raise ValueError("Invalid PPO checkpoint ZIP")
    with zipfile.ZipFile(model_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Corrupt checkpoint ZIP member")
    return {"model_id": entry["id"], "sha256": actual, "bytes": model_path.stat().st_size,
            "integrity": "sha256_and_zip_ok",
            "load_and_optimizer_resume_verified_by_this_check": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--model-id")
    parser.add_argument("--asset", type=Path)
    args = parser.parse_args()
    data, by_id = load_registry(args.registry)
    if (args.model_id is None) != (args.asset is None):
        parser.error("--model-id and --asset must be supplied together")
    if args.model_id:
        if args.model_id not in by_id:
            parser.error("Model not registered")
        print(json.dumps(verify_asset(by_id[args.model_id], args.asset), sort_keys=True))
    else:
        print(json.dumps({"validated": len(by_id), "latest": data["latest"],
                          "champion": data["champion"]}, sort_keys=True))


if __name__ == "__main__":
    main()
