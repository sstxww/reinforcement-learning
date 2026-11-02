"""Fail-closed offline index and digest checks for versioned PPO checkpoints.

Release publication, downloaded byte integrity, SB3 loading, actual optimizer
continuation and full eight-seat games are separate verification gates.
This module never performs network requests or promotes models implicitly.
"""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path
from typing import Any
from .contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES

RELEASE_PREFIX = "https://github.com/sstxww/reinforcement-learning/releases/download/"
ROLES = frozenset({"Champion", "Challenger", "Latest", "Population", "Rejected"})
HEX_256 = re.compile(r"[0-9a-f]{64}\Z")

def digest_file(path: Path) -> str:
    """Stream large files rather than reading full checkpoint archives."""
    hasher = hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda: src.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()

def _bool_checks(model: dict[str, Any]) -> None:
    checks = model.get("verification")
    required = ("release_indexed", "weights_download_hash_checked",
                "metadata_download_hash_checked", "sb3_load_checked",
                "training_resume_checked", "full_game_checked")
    if not isinstance(checks, dict) or any(type(checks.get(k)) is not bool for k in required):
        raise ValueError(f"Model {model.get('id')}: missing explicit verification flags")
    if model["role"] == "Champion" and not all(checks[k] for k in required):
        raise ValueError("Champion requires every verification gate")

def validate_registry(registry: dict[str, Any]) -> dict[str, Any]:
    if type(registry.get("schema")) is not int or registry["schema"] != 1:
        raise ValueError("Unsupported registry schema")
    rows = registry.get("models")
    if not isinstance(rows, list):
        raise ValueError("models must be a list")
    ids: set[str] = set()
    for entry in rows:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"]:
            raise ValueError("Missing model id")
        ident = entry["id"]
        if ident in ids:
            raise ValueError(f"Duplicate model id: {ident}")
        ids.add(ident)
        if entry.get("role") not in ROLES:
            raise ValueError(f"Unsupported model role for {ident}")
        steps = entry.get("train_steps")
        if steps is not None and (type(steps) is not int or steps < 0):
            raise ValueError(f"Invalid train_steps for {ident}")
        for field, filename in (("weights", "model.zip"), ("metadata", "model.metadata.json")):
            descriptor = entry.get(field)
            if (not isinstance(descriptor, dict)
                    or not isinstance(descriptor.get("sha256"), str)
                    or not HEX_256.fullmatch(descriptor["sha256"])):
                raise ValueError(f"Missing SHA256 for {ident}/{field}")
            expected = f"{RELEASE_PREFIX}{ident}/{filename}"
            if descriptor.get("url") != expected:
                raise ValueError(f"Unexpected release URL for {ident}/{field}")
        _bool_checks(entry)
    for entry in rows:
        parent = entry.get("parent_id")
        if parent is not None and (
                not isinstance(parent, str) or parent not in ids or parent == entry["id"]):
            raise ValueError(f"Invalid parent model for {entry['id']}")
    champs = [entry["id"] for entry in rows if entry["role"] == "Champion"]
    champion_id = registry.get("champion_id")
    if len(champs) > 1 or (champion_id is None and champs) or (
            champion_id is not None and champs != [champion_id]):
        raise ValueError("Champion ID must reference exactly one fully verified model")
    latest = registry.get("latest_resumable_id")
    if latest is not None:
        item = next((m for m in rows if m["id"] == latest), None)
        if item is None or not item["verification"]["training_resume_checked"]:
            raise ValueError("Latest resumable checkpoint requires a real resume check")
    return registry

def verify_local(registry: dict[str, Any], model_id: str, weights: Path,
                 metadata: Path, check_load: bool = False) -> dict[str, Any]:
    """Verify both digests and engine metadata; optional SB3 load is not PPO training."""
    validate_registry(registry)
    item = next((m for m in registry["models"] if m["id"] == model_id), None)
    if item is None:
        raise ValueError(f"Unknown model id: {model_id}")
    for path, descriptor in ((weights, item["weights"]), (metadata, item["metadata"])):
        actual = digest_file(path)
        if not hmac.compare_digest(actual, descriptor["sha256"]):
            raise ValueError(f"SHA256 mismatch for {path.name}")
    meta = json.loads(metadata.read_text(encoding="utf-8"))
    engine = meta.get("engine")
    expected = {"version": "1.1.0", "source_hash": ENGINE_HASH,
                "features": FEATURES, "cards": CARDS, "actions": ACTIONS}
    if not isinstance(engine, dict) or any(engine.get(k) != v for k, v in expected.items()):
        raise ValueError("Checkpoint engine/observation mismatch")
    steps = item.get("train_steps")
    if steps is not None and meta.get("total_timesteps") != steps:
        raise ValueError("Checkpoint training-step metadata mismatch")
    result = {"model_id": model_id, "weights_sha256_ok": True,
              "metadata_sha256_ok": True, "engine_metadata_ok": True,
              "sb3_load_checked": False, "training_resume_checked": False}
    if check_load:
        from .contract import verify_engine
        from sb3_contrib import MaskablePPO
        verify_engine()
        model = MaskablePPO.load(str(weights), device="cpu")
        if steps is not None and model.num_timesteps != steps:
            raise ValueError("Loaded PPO training-step mismatch")
        result["sb3_load_checked"] = True
    return result

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--model-id")
    parser.add_argument("--weights", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--check-load", action="store_true")
    args = parser.parse_args()
    registry = validate_registry(json.loads(args.registry.read_text(encoding="utf-8")))
    if args.model_id or args.weights or args.metadata or args.check_load:
        if not all((args.model_id, args.weights, args.metadata)):
            parser.error("--model-id, --weights and --metadata must be supplied together")
        report = verify_local(registry, args.model_id, args.weights, args.metadata, args.check_load)
    else:
        report = {"registry_models": len(registry["models"]),
                  "champion_id": registry["champion_id"],
                  "latest_resumable_id": registry["latest_resumable_id"],
                  "note": "Release-indexed digests are not independent downloaded-byte or resume checks"}
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
