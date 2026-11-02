"""Offline Release registry validation: byte integrity is not PPO restore evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ENGINE = {"version": "1.1.0", "source_hash": "6d8712c93022ba11",
          "features": 4017, "cards": 447, "actions": 245}
ROLES = {"Challenger", "Latest", "Population", "Rejected"}
HEX = re.compile(r"^[0-9a-f]{64}$")
RELEASE = "https://github.com/sstxww/reinforcement-learning/releases/download/"

class CatalogError(ValueError):
    pass

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def validate_catalog(raw: dict) -> dict:
    if not isinstance(raw, dict) or raw.get("schema") != 1 or not isinstance(raw.get("models"), list):
        raise CatalogError("Invalid catalog schema")
    indexed = {}
    for entry in raw["models"]:
        if not isinstance(entry, dict):
            raise CatalogError("Invalid model entry")
        name = entry.get("id")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}", name):
            raise CatalogError("Invalid model ID")
        if name in indexed:
            raise CatalogError("Duplicate model ID")
        if entry.get("role") not in ROLES or entry.get("engine") != ENGINE:
            raise CatalogError("Invalid role or engine fingerprint")
        if type(entry.get("total_timesteps")) is not int or entry["total_timesteps"] < 0:
            raise CatalogError("Invalid training step count")
        if not isinstance(entry.get("architecture"), str) or not entry["architecture"]:
            raise CatalogError("Missing architecture")
        for key in ("download_verified", "load_verified", "resume_verified",
                    "full_match_verified", "paired_improvement_verified"):
            if type(entry.get(key)) is not bool:
                raise CatalogError("Missing verification flag " + key)
        assets = entry.get("assets")
        if not isinstance(assets, dict) or set(assets) != {"weights", "metadata"}:
            raise CatalogError("Missing asset manifest")
        for asset in assets.values():
            if not isinstance(asset, dict) or not isinstance(asset.get("url"), str):
                raise CatalogError("Missing asset URL")
            if not asset["url"].startswith(RELEASE) or not HEX.fullmatch(str(asset.get("sha256", ""))):
                raise CatalogError("Bad release origin or digest")
        if entry["resume_verified"] and not entry["load_verified"]:
            raise CatalogError("Resume requires load verification")
        indexed[name] = entry
    for entry in raw["models"]:
        parent = entry.get("parent")
        if parent is not None:
            if parent not in indexed or parent == entry["id"]:
                raise CatalogError("Invalid parent model")
            if indexed[parent]["total_timesteps"] >= entry["total_timesteps"]:
                raise CatalogError("Steps do not advance from parent")
    for pointer in ("champion", "latest"):
        if raw.get(pointer) is not None and raw[pointer] not in indexed:
            raise CatalogError("Pointer references missing model")
    if raw.get("latest") is not None:
        e = indexed[raw["latest"]]
        if not (e["download_verified"] and e["load_verified"] and e["resume_verified"]):
            raise CatalogError("Unverified model cannot be Latest")
    if raw.get("champion") is not None:
        e = indexed[raw["champion"]]
        required = ("download_verified", "load_verified", "resume_verified",
                    "full_match_verified", "paired_improvement_verified")
        if not all(e[k] for k in required):
            raise CatalogError("Unverified model cannot be Champion")
    return indexed

def verify_files(entry: dict, weights: Path, metadata: Path) -> dict:
    """Check exact bytes, zip CRCs and metadata; never deserialize a PPO model."""
    if not weights.is_file() or not metadata.is_file():
        raise CatalogError("Both asset files are required")
    for key, path in (("weights", weights), ("metadata", metadata)):
        if digest(path) != entry["assets"][key]["sha256"]:
            raise CatalogError(key + " SHA256 mismatch")
    if not zipfile.is_zipfile(weights):
        raise CatalogError("Weights not a ZIP")
    try:
        with zipfile.ZipFile(weights) as z:
            if not z.namelist() or z.testzip() is not None:
                raise CatalogError("Corrupt ZIP")
    except (zipfile.BadZipFile, OSError) as ex:
        raise CatalogError("Unreadable checkpoint ZIP") from ex
    try:
        info = json.loads(metadata.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as ex:
        raise CatalogError("Unreadable metadata") from ex
    if not isinstance(info, dict) or info.get("algorithm") != "MaskablePPO":
        raise CatalogError("Incompatible algorithm")
    if info.get("total_timesteps") != entry["total_timesteps"]:
        raise CatalogError("Step count mismatch")
    engine = info.get("engine")
    if not isinstance(engine, dict) or any(engine.get(k) != v for k, v in ENGINE.items()):
        raise CatalogError("Incompatible engine / action vocabulary")
    return {"id": entry["id"], "sha256_verified": True, "zip_crc_verified": True,
            "metadata_verified": True, "model_load_tested": False,
            "optimizer_resume_tested": False, "real_match_tested": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--model-id")
    parser.add_argument("--weights", type=Path)
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()
    registry = json.loads(args.catalog.read_text(encoding="utf-8"))
    records = validate_catalog(registry)
    if args.model_id is None:
        if args.weights is not None or args.metadata is not None:
            parser.error("Files require model id")
        out = {"entries": len(records), "champion": registry.get("champion"),
               "latest": registry.get("latest"), "ids": sorted(records)}
    else:
        if args.model_id not in records or args.weights is None or args.metadata is None:
            parser.error("Known model id and two files required")
        out = verify_files(records[args.model_id], args.weights, args.metadata)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
