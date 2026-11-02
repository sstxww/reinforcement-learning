"""Fail-closed, content-addressed PPO checkpoint manifests.

This module never trains, uploads or promotes models. A Release listing alone
is not evidence that weights can be loaded or resumed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

from .contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES

SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,79}\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
ROLES = {"Latest", "Challenger", "Population", "Rejected"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_metadata(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Training metadata must be an object")
    engine = data.get("engine")
    if not isinstance(engine, dict) or any(
        engine.get(k) != v for k, v in {
            "version": "1.1.0", "source_hash": ENGINE_HASH,
            "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
        }.items()
    ):
        raise ValueError("Checkpoint engine or observation layout mismatch")
    if data.get("algorithm") != "MaskablePPO":
        raise ValueError("Unsupported algorithm")
    steps = data.get("total_timesteps")
    if type(steps) is not int or steps <= 0:
        raise ValueError("Invalid cumulative training steps")
    return data


def create_manifest(model: Path, metadata: Path, *, model_id: str,
                    source_commit: str, role: str = "Challenger",
                    parent_model_id: str | None = None,
                    storage_uri: str | None = None) -> dict:
    if not ID_RE.fullmatch(model_id):
        raise ValueError("Invalid immutable model ID")
    if not COMMIT_RE.fullmatch(source_commit):
        raise ValueError("Source must be a full 40-character commit SHA")
    if role not in ROLES:
        raise ValueError("Champion cannot be assigned without competitive gates")
    if parent_model_id is not None and not ID_RE.fullmatch(parent_model_id):
        raise ValueError("Invalid parent model ID")
    if parent_model_id == model_id:
        raise ValueError("A checkpoint cannot be its own parent")
    if storage_uri is not None and not storage_uri.startswith("https://"):
        raise ValueError("Storage URI must be HTTPS; do not publish credentials")
    if not model.is_file() or model.suffix != ".zip":
        raise FileNotFoundError("Existing .zip model file required")
    if not metadata.is_file():
        raise FileNotFoundError("Training metadata is required")
    info = read_metadata(metadata)
    return {
        "schema": 1, "model_id": model_id, "role": role,
        "source_commit": source_commit, "parent_model_id": parent_model_id,
        "algorithm": info["algorithm"], "engine": info["engine"],
        "total_timesteps": info["total_timesteps"],
        "weights_sha256": sha256_file(model),
        "metadata_sha256": sha256_file(metadata),
        "weights_bytes": model.stat().st_size,
        "storage_uri": storage_uri,
        "storage_verified": False, "model_load_verified": False,
        "optimizer_resume_verified": False,
        "full_eight_seat_match_verified": False,
        "competitive_evaluation_verified": False,
        "champion_eligible": False,
    }


def verify_manifest(manifest: dict, model: Path, metadata: Path) -> dict:
    if not isinstance(manifest, dict) or manifest.get("schema") != 1:
        raise ValueError("Unsupported checkpoint manifest")
    if not ID_RE.fullmatch(str(manifest.get("model_id", ""))):
        raise ValueError("Invalid manifest model ID")
    if manifest.get("role") not in ROLES:
        raise ValueError("Manifest claims an unverified role")
    if not COMMIT_RE.fullmatch(str(manifest.get("source_commit", ""))):
        raise ValueError("Invalid source commit")
    info = read_metadata(metadata)
    if info["engine"] != manifest.get("engine"):
        raise ValueError("Engine metadata does not match manifest")
    if info["total_timesteps"] != manifest.get("total_timesteps"):
        raise ValueError("Cumulative training steps differ")
    if info["algorithm"] != manifest.get("algorithm"):
        raise ValueError("Algorithm changed")
    for key, path in (("weights_sha256", model), ("metadata_sha256", metadata)):
        expected = manifest.get(key)
        if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
            raise ValueError(f"Missing or invalid {key}")
        if sha256_file(path) != expected:
            raise ValueError(f"{key} mismatch: refuse checkpoint")
    if model.stat().st_size != manifest.get("weights_bytes"):
        raise ValueError("Model byte count mismatch")
    return {"model_id": manifest["model_id"], "integrity": "passed",
            "load_tested": False, "optimizer_resume_tested": False}


def atomic_json(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".registry-", suffix=".tmp", delete=False) as tmp:
            name = tmp.name
            json.dump(document, tmp, indent=2, sort_keys=True)
            tmp.write("\n")
        os.replace(name, path)
    finally:
        if name is not None and os.path.exists(name):
            os.unlink(name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for cmd in ("record", "verify"):
        p = commands.add_parser(cmd)
        p.add_argument("--model", type=Path, required=True)
        p.add_argument("--metadata", type=Path, required=True)
        p.add_argument("--manifest", type=Path, required=True)
        if cmd == "record":
            p.add_argument("--model-id", required=True)
            p.add_argument("--source-commit", required=True)
            p.add_argument("--role", choices=sorted(ROLES), default="Challenger")
            p.add_argument("--parent-model-id")
            p.add_argument("--storage-uri")
    args = parser.parse_args()
    if args.command == "record":
        if args.manifest.exists():
            raise FileExistsError("Immutable model manifest already exists")
        output = create_manifest(args.model, args.metadata, model_id=args.model_id,
                                 source_commit=args.source_commit, role=args.role,
                                 parent_model_id=args.parent_model_id,
                                 storage_uri=args.storage_uri)
        atomic_json(args.manifest, output)
    else:
        record = json.loads(args.manifest.read_text(encoding="utf-8"))
        output = verify_manifest(record, args.model, args.metadata)
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
