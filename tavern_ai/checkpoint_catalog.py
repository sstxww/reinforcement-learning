"""Complement main registry: verify BOTH Release files and ZIP/engine integrity.

Main's registry is authoritative. 'latest' means latest *unpromoted
experimental release*, never an independently verified resumable Champion.
Checks here do not deserialize PPO weights or verify optimizer restoration.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .registry_integrity import validate_registry, verify_checkpoint

ENGINE = {"version": "1.1.0", "source_hash": "6d8712c93022ba11",
          "features": 4017, "cards": 447, "actions": 245}
# GitHub Release API digest claims. Verify actual bytes before relying on them.
METADATA_SHA256 = {
    "v1-learning-9eada5801f99": "74a6b25af97087a003d74a3b8e274ac9dbf95bf91fa409eb0fea1a5cc05e5ac6",
    "v1-learning-165a76a18afb": "086e5303989a6ed3e65729803af664168f865403584124c6a4918e54f2118937",
    "v1-learning-resume-41413508653": "5562c29610044263ed8b632c84fc939d6e68bad11616911344e86f450692c010",
    "v2-learning-41413557445": "6f0b433191a8242dcedc627f6be49d1551a82788ce7bfd8e60416ede8146acc0",
}
HEX = re.compile(r"^[a-f0-9]{64}$")

class CatalogError(ValueError):
    """Invalid Release bytes/metadata; stop before training."""

def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def validate_catalog(raw: dict) -> dict:
    """Re-use main's single canonical schema; never create a second registry."""
    try:
        validate_registry(raw)
    except (ValueError, TypeError, KeyError) as exc:
        raise CatalogError(str(exc)) from exc
    indexed = {entry["id"]: entry for entry in raw["candidates"]}
    for model_id, value in METADATA_SHA256.items():
        if not HEX.fullmatch(value):
            raise CatalogError("Bad metadata digest: " + model_id)
    if raw.get("best") is not None or raw.get("champion") is not None:
        raise CatalogError("Unproven Champion/Best")
    return indexed

def verify_files(entry: dict, weights: Path, metadata: Path,
                 expected_metadata_sha256: str) -> dict:
    """Verify checkpoint+metadata digests, ZIP CRC, timesteps and engine shape."""
    if not weights.is_file() or not metadata.is_file():
        raise CatalogError("Both Release asset files are required")
    if not isinstance(expected_metadata_sha256, str) or not HEX.fullmatch(expected_metadata_sha256):
        raise CatalogError("Missing expected metadata digest")
    try:
        verify_checkpoint(weights, entry["checkpoint_sha256"])
    except (ValueError, OSError) as exc:
        raise CatalogError("Weights SHA256 mismatch") from exc
    if _digest(metadata) != expected_metadata_sha256:
        raise CatalogError("Metadata SHA256 mismatch")
    if not zipfile.is_zipfile(weights):
        raise CatalogError("Weights not a ZIP")
    try:
        with zipfile.ZipFile(weights) as archive:
            if not archive.namelist() or archive.testzip() is not None:
                raise CatalogError("Corrupt checkpoint ZIP")
    except (zipfile.BadZipFile, OSError) as exc:
        raise CatalogError("Unreadable checkpoint ZIP") from exc
    try:
        info = json.loads(metadata.read_text(encoding="utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise CatalogError("Invalid model metadata") from exc
    if not isinstance(info, dict) or info.get("algorithm") != "MaskablePPO":
        raise CatalogError("Wrong checkpoint algorithm")
    if info.get("total_timesteps") != entry["training_steps"]:
        raise CatalogError("Checkpoint step count mismatch")
    state = info.get("engine")
    if not isinstance(state, dict) or any(state.get(k) != v for k, v in ENGINE.items()):
        raise CatalogError("Checkpoint engine or action vocabulary mismatch")
    return {"model_id": entry["id"], "sha256_verified": True,
            "zip_crc_verified": True, "metadata_contract_verified": True,
            "model_deserialized": False, "optimizer_resume_tested": False,
            "model_only_full_game_tested": False}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--model-id")
    parser.add_argument("--weights", type=Path)
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()
    raw = json.loads(args.catalog.read_text(encoding="utf-8"))
    index = validate_catalog(raw)
    if args.model_id is None:
        if args.weights is not None or args.metadata is not None:
            parser.error("Local files require --model-id")
        output = {"candidates": len(index), "best": None,
                  "latest_experimental_unpromoted": raw["latest"]["id"],
                  "actual_checkpoint_bytes_checked": False}
    else:
        if args.model_id not in index or args.weights is None or args.metadata is None:
            parser.error("Known model ID and both files required")
        if args.model_id not in METADATA_SHA256:
            parser.error("No pinned metadata Release digest for this model")
        output = verify_files(index[args.model_id], args.weights, args.metadata,
                              METADATA_SHA256[args.model_id])
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
