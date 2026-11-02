"""Auditable, fail-closed local checkpoint verification for archived TavernGym Releases.

Never interprets GitHub release presence as load, resume, or game success.
Designed as a narrow V5 integration of the registry proposed in PR #8.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_registry(path: Path) -> dict:
    registry = json.loads(path.read_text(encoding="utf-8"))
    if registry.get("schema") != 1 or registry.get("repository") != "sstxww/reinforcement-learning":
        raise ValueError("Unsupported model registry")
    if registry.get("best") is not None:
        raise ValueError("This conservative V5 audit does not authorize Champion promotion")
    engine = registry.get("engine", {})
    if (engine.get("version"), engine.get("source_hash"), engine.get("float_features"),
            engine.get("card_slots"), engine.get("action_count")) != (
            "1.1.0", "6d8712c93022ba11", 4017, 447, 245):
        raise ValueError("Unsupported pinned engine contract")
    releases = registry.get("github_release_asset_inventory")
    if not isinstance(releases, list) or not releases:
        raise ValueError("Missing Release inventory")
    tags = [entry.get("tag") for entry in releases]
    if any(not isinstance(tag, str) or not tag for tag in tags) or len(set(tags)) != len(tags):
        raise ValueError("Invalid or duplicate Release tag")
    for item in releases:
        asset = item.get("model_asset")
        digest = asset.get("github_api_sha256") if isinstance(asset, dict) else None
        if not isinstance(digest, str) or not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
            raise ValueError("Release missing full API SHA256 digest")
        if item.get("metadata_asset_present") is not True:
            raise ValueError("Release metadata asset missing")
    return registry


def verify_local_release(registry: dict, tag: str, model: Path, metadata: Path) -> dict:
    item = next((x for x in registry["github_release_asset_inventory"] if x["tag"] == tag), None)
    if item is None:
        raise ValueError("Unregistered Release tag")
    if not model.is_file() or not metadata.is_file():
        raise FileNotFoundError("Both Release model and metadata must be downloaded")
    expected = item["model_asset"]["github_api_sha256"].split(":", 1)[1]
    actual = sha256_file(model)
    if actual != expected:
        raise ValueError("Release binary checksum mismatch")
    meta = json.loads(metadata.read_text(encoding="utf-8"))
    if meta.get("checkpoint_sha256") != actual:
        raise ValueError("Metadata checkpoint SHA256 mismatch")
    engine = meta.get("engine")
    pinned = registry["engine"]
    if not isinstance(engine, dict) or (engine.get("version"), engine.get("source_hash"),
            engine.get("features"), engine.get("cards"), engine.get("actions")) != (
            pinned["version"], pinned["source_hash"], pinned["float_features"],
            pinned["card_slots"], pinned["action_count"]):
        raise ValueError("Metadata engine layout is incompatible")
    if meta.get("compatibility", {}).get("engine") != engine:
        raise ValueError("Metadata lacks exact engine compatibility")
    steps = meta.get("total_timesteps")
    if type(steps) is not int or steps <= 0:
        raise ValueError("Missing valid total training steps")
    latest = registry.get("latest")
    if isinstance(latest, dict) and latest.get("release_tag") == tag:
        if latest.get("training_steps") != steps or latest.get("checkpoint_sha256") != actual:
            raise ValueError("Latest registry/Release lineage mismatch")
    return {
        "schema": 1, "release_tag": tag, "checkpoint_sha256": actual,
        "metadata_sha256": sha256_file(metadata), "bytes": model.stat().st_size,
        "training_steps": steps, "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "binary_sha256_verified": True, "metadata_compatible": True,
        "model_load_tested": False, "resume_training_tested": False,
        "full_game_tested": False, "champion_promoted": False,
        "claim": "Verified downloaded bytes + metadata only; NOT load/resume/full-game or strength",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    p.add_argument("--release-tag")
    p.add_argument("--model", type=Path)
    p.add_argument("--metadata", type=Path)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    registry = load_registry(args.registry)
    if args.release_tag:
        if args.model is None or args.metadata is None:
            p.error("--release-tag requires --model and --metadata")
        result = verify_local_release(registry, args.release_tag, args.model, args.metadata)
    else:
        result = {"schema": 1, "inventory_entries": len(registry["github_release_asset_inventory"]),
                  "champion": None, "downloaded_binary_verified": False}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
