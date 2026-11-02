"""Fail-closed audit of published PPO checkpoints; never auto-promote a model.

This checks a LOCAL, already downloaded Release asset against the immutable
SHA-256 catalog and pinned engine metadata. It does NOT claim that a model
plays well or that a checkpoint has passed a real resume test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES

RELEASE_PREFIX = "https://github.com/sstxww/reinforcement-learning/releases/download/"
_SHA = re.compile(r"^[0-9a-f]{64}$")


def read_registry(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or obj.get("schema") != 1:
        raise ValueError("Unsupported model registry schema")
    entries = obj.get("models")
    roles = obj.get("roles")
    if not isinstance(entries, list) or not isinstance(roles, dict):
        raise ValueError("Missing models or roles")
    ids = []
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("Malformed model entry")
        model_id = item.get("id")
        digest = item.get("sha256")
        url = item.get("url")
        if not isinstance(model_id, str) or not model_id:
            raise ValueError("Empty model id")
        if not isinstance(digest, str) or not _SHA.fullmatch(digest):
            raise ValueError(f"Bad SHA-256 for {model_id}")
        if not isinstance(url, str) or not url.startswith(RELEASE_PREFIX):
            raise ValueError(f"Untrusted Release URL for {model_id}")
        if not url.endswith("/model.zip"):
            raise ValueError(f"Expected Release model.zip for {model_id}")
        if url.split("/")[-2] != model_id:
            raise ValueError(f"Release tag mismatch for {model_id}")
        if item.get("review_status") != "unverified" and item.get("review_status") != "verified":
            raise ValueError(f"Unknown review status for {model_id}")
        ids.append(model_id)
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate model IDs")
    for key in ("champion", "challenger", "latest"):
        if roles.get(key) is not None and roles[key] not in ids:
            raise ValueError(f"Role {key} references an unknown model")
    # Named population/rejected pools must reference known immutable model IDs.
    for role in ("population", "rejected"):
        members = roles.get(role, [])
        if not isinstance(members, list) or len(members) != len(set(
                member for member in members if isinstance(member, str))):
            raise ValueError(f"Invalid {role} model pool")
        if any(not isinstance(member, str) or member not in ids for member in members):
            raise ValueError(f"Unknown model in {role} pool")
    if roles.get("champion") is not None:
        selected = next(e for e in entries if e["id"] == roles["champion"])
        if selected["review_status"] != "verified":
            raise ValueError("Unverified checkpoint cannot be Champion")
        # A human-entered 'verified' label alone must never activate Champion.
        # These explicit evidence flags are NECESSARY but not SUFFICIENT:
        # integrators must still check linked original runs/receipts and source.
        gates = ("hash_verified", "load_verified", "optimizer_resume_verified",
                 "complete_match_verified", "competitive_gain_verified")
        missing = [key for key in gates if selected.get(key) is not True]
        if missing:
            raise ValueError("Champion lacks required evidence: " + ", ".join(missing))
    return obj


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_local(model: dict, archive: Path, metadata: Path, *, load: bool = False) -> dict:
    """Verify bytes, zip structure, metadata and optionally a CPU model load.

    Zip/metadata verification is not a substitute for real inference, PPO
    continuation, complete-match tests or a durable storage audit.
    """
    if not archive.is_file() or not metadata.is_file():
        raise FileNotFoundError("Both model.zip and model.metadata.json are required")
    actual = sha256_file(archive)
    if actual != model["sha256"]:
        raise ValueError(f"Checkpoint SHA-256 mismatch: {model['id']}")
    try:
        with zipfile.ZipFile(archive) as z:
            names = set(z.namelist())
            necessary = {"data", "policy.pth", "policy.optimizer.pth"}
            if not necessary.issubset(names):
                raise ValueError("Archive lacks policy/optimizer state required for continuation")
            if sum(i.file_size for i in z.infolist()) > 1024 * 1024 * 1024:
                raise ValueError("Checkpoint expands beyond audit limit")
            corrupt = z.testzip()
            if corrupt is not None:
                raise ValueError(f"Corrupt checkpoint archive member: {corrupt}")
    except zipfile.BadZipFile as exc:
        raise ValueError("Invalid checkpoint ZIP") from exc
    meta = json.loads(metadata.read_text(encoding="utf-8"))
    if not isinstance(meta, dict) or meta.get("schema") not in (1, 2):
        raise ValueError("Invalid checkpoint metadata schema")
    engine = meta.get("engine")
    if not isinstance(engine, dict):
        raise ValueError("Missing engine metadata")
    expected = {"version": "1.1.0", "source_hash": ENGINE_HASH,
                "features": FEATURES, "cards": CARDS, "actions": ACTIONS}
    for k, expected_value in expected.items():
        if engine.get(k) != expected_value:
            raise ValueError(f"Incompatible checkpoint engine: {k}")
    if meta.get("schema") == 2:
        compatibility = meta.get("compatibility")
        if not isinstance(compatibility, dict) or compatibility.get("engine") != engine:
            raise ValueError("Incompatible V2 checkpoint compatibility object")
    if meta.get("checkpoint_sha256") is not None and meta["checkpoint_sha256"] != actual:
        raise ValueError("Checkpoint metadata SHA-256 mismatch")
    if meta.get("algorithm") != "MaskablePPO":
        raise ValueError("Unexpected checkpoint algorithm")
    if type(meta.get("total_timesteps")) is not int or meta["total_timesteps"] < 1:
        raise ValueError("Missing positive trained-step count")
    reported = model.get("reported_total_timesteps")
    if reported is not None and meta["total_timesteps"] != reported:
        raise ValueError("Step-count discrepancy with Release catalog")
    if load:
        from sb3_contrib import MaskablePPO
        loaded = MaskablePPO.load(str(archive), device="cpu")
        if loaded.action_space.n != ACTIONS:
            raise ValueError("Checkpoint action space mismatch")
        spaces = loaded.observation_space.spaces
        if spaces["features"].shape != (FEATURES,) or spaces["cards"].shape != (CARDS,):
            raise ValueError("Checkpoint observation space mismatch")
    return {"model_id": model["id"], "sha256": actual, "metadata_steps": meta["total_timesteps"],
            "hash_verified": True, "zip_integrity_verified": True,
            "optimizer_state_present": True, "engine_metadata_verified": True,
            "cpu_load_verified": load, "resume_test_verified": False,
            "full_match_verified": False, "strength_gain_verified": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("models/release_inventory_v5.json"))
    parser.add_argument("--model-id")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--load", action="store_true")
    args = parser.parse_args()
    catalog = read_registry(args.registry)
    if args.model_id is None:
        if args.checkpoint or args.metadata or args.load:
            parser.error("--model-id is required with local verification")
        print(json.dumps({"models": len(catalog["models"]), "roles": catalog["roles"]}))
        return
    selected = next((m for m in catalog["models"] if m["id"] == args.model_id), None)
    if selected is None:
        parser.error("Unknown model ID")
    if args.checkpoint is None or args.metadata is None:
        parser.error("--checkpoint and --metadata are required together")
    print(json.dumps(verify_local(selected, args.checkpoint, args.metadata, load=args.load), sort_keys=True))


if __name__ == "__main__":
    main()
