"""Additive Release *asset-byte* audit for the canonical models/registry.json.

An upstream Release asset API digest is an expected value, not proof of
download, SB3 loading, optimizer continuation, or full-match capability.
This module never alters the champion, training code or canonical registry.
"""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

from .contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES
from .registry_integrity import validate_registry as validate_canonical

RELEASE_PREFIX = "https://github.com/sstxww/reinforcement-learning/releases/download/"
HEX = re.compile(r"^[a-f0-9]{64}$")

def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def validate_asset_index(index: dict, canonical: dict) -> dict:
    """Check indexed model/metadata digests against the existing canonical registry."""
    validate_canonical(canonical)
    if type(index.get("schema")) is not int or index["schema"] != 1:
        raise ValueError("Unsupported Release asset index schema")
    assets = index.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("Missing Release asset records")
    seen = set()
    for record in assets:
        if not isinstance(record, dict):
            raise ValueError("Malformed Release asset record")
        ident = record.get("id")
        if not isinstance(ident, str) or not ident or ident in seen:
            raise ValueError("Missing or duplicate Release ID")
        seen.add(ident)
        for field, file_name in (("weights", "model.zip"), ("metadata", "model.metadata.json")):
            entry = record.get(field)
            if not isinstance(entry, dict):
                raise ValueError(f"Missing {field} for {ident}")
            if (entry.get("url") != f"{RELEASE_PREFIX}{ident}/{file_name}"
                    or not isinstance(entry.get("sha256"), str)
                    or not HEX.fullmatch(entry["sha256"])):
                raise ValueError(f"Invalid source URL or SHA256 for {ident}/{field}")
        for field in ("weights_bytes_verified", "metadata_bytes_verified",
                      "model_load_verified", "optimizer_resume_verified"):
            if type(record.get(field)) is not bool:
                raise ValueError(f"Missing explicit {field} flag for {ident}")
    for candidate in canonical["candidates"]:
        ident = candidate["id"]
        asset = next((a for a in assets if a["id"] == ident), None)
        if asset is None:
            raise ValueError(f"Canonical candidate missing asset hashes: {ident}")
        if not hmac.compare_digest(asset["weights"]["sha256"],
                                   candidate["checkpoint_sha256"]):
            raise ValueError(f"Canonical weight SHA256 mismatch for {ident}")
        if candidate.get("independent_release_resume_tested") is False and asset["optimizer_resume_verified"]:
            raise ValueError(f"Contradictory resume verified flag: {ident}")
    if canonical["best"] is not None or canonical["champion"] is not None:
        raise ValueError("No validated Champion is registered")
    return {"indexed_releases": len(assets), "canonical_candidates_matched":
            len(canonical["candidates"]), "does_not_claim_verification": True}

def verify_local(index: dict, canonical: dict, model_id: str, weights: Path,
                 metadata: Path, check_load: bool = False) -> dict:
    """Read actual local bytes. check_load is not a resume or full-game test."""
    validate_asset_index(index, canonical)
    record = next((a for a in index["assets"] if a["id"] == model_id), None)
    if record is None:
        raise ValueError(f"Unknown Release ID: {model_id}")
    for path, descriptor in ((weights, record["weights"]),
                             (metadata, record["metadata"])):
        if not hmac.compare_digest(digest_file(path), descriptor["sha256"]):
            raise ValueError(f"SHA256 mismatch: {path.name}")
    doc = json.loads(metadata.read_text(encoding="utf-8"))
    engine = doc.get("engine")
    expected = {"version": "1.1.0", "source_hash": ENGINE_HASH,
                "features": FEATURES, "cards": CARDS, "actions": ACTIONS}
    if not isinstance(engine, dict) or any(engine.get(k) != v for k, v in expected.items()):
        raise ValueError("Incompatible model metadata engine/observation")
    candidate = next((m for m in canonical["candidates"] if m["id"] == model_id), None)
    if candidate and doc.get("total_timesteps") != candidate["training_steps"]:
        raise ValueError("Model training step counter mismatch")
    result = {"release_id": model_id, "weight_bytes_sha256_verified": True,
              "metadata_bytes_sha256_verified": True, "engine_metadata_verified": True,
              "sb3_load_checked": False, "optimizer_resume_checked": False,
              "complete_game_checked": False}
    if check_load:
        from sb3_contrib import MaskablePPO
        from .contract import verify_engine
        verify_engine()
        model = MaskablePPO.load(str(weights), device="cpu")
        if candidate and model.num_timesteps != candidate["training_steps"]:
            raise ValueError("Loaded SB3 model steps mismatch")
        result["sb3_load_checked"] = True
    return result

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=Path("models/release_asset_digests.json"))
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--model-id", type=str)
    parser.add_argument("--weights", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--check-load", action="store_true")
    args = parser.parse_args()
    index = json.loads(args.index.read_text(encoding="utf-8"))
    canonical = json.loads(args.registry.read_text(encoding="utf-8"))
    report = validate_asset_index(index, canonical)
    if args.model_id or args.weights or args.metadata or args.check_load:
        if not all((args.model_id, args.weights, args.metadata)):
            parser.error("Require --model-id, --weights and --metadata together")
        report = verify_local(index, canonical, args.model_id, args.weights, args.metadata, args.check_load)
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
