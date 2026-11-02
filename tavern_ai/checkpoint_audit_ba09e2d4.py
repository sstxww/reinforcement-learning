"""Fail-closed, offline structural integrity gate for TavernGym PPO checkpoints.

This deliberately does not deserialize PyTorch weights or claim that PPO resume works.
Use an actual engine-backed restore + continuation job before marking load_verified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES


REQUIRED_MEMBERS = {"data", "policy.pth", "policy.optimizer.pth"}
MAX_CHECKPOINT_BYTES = 512 * 1024 * 1024


def audit_checkpoint(checkpoint: Path, metadata: Path, expected_sha256: str) -> dict:
    """Verify expected bytes, metadata compatibility and SB3 archive structure."""
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError("A pinned lowercase SHA256 digest is mandatory")
    if not checkpoint.is_file() or not metadata.is_file():
        raise FileNotFoundError("Checkpoint and adjacent metadata must both exist")
    size = checkpoint.stat().st_size
    if size <= 0 or size > MAX_CHECKPOINT_BYTES:
        raise ValueError("Checkpoint archive size is outside the bounded audit range")
    digest = hashlib.sha256()
    with checkpoint.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != expected_sha256:
        raise ValueError("Checkpoint SHA256 mismatch")
    info = json.loads(metadata.read_text(encoding="utf-8"))
    if not isinstance(info, dict) or info.get("schema") != 1:
        raise ValueError("Unsupported checkpoint metadata schema")
    engine = info.get("engine")
    if not isinstance(engine, dict):
        raise ValueError("Missing pinned engine metadata")
    checks = {
        "version": "1.1.0",
        "source_hash": ENGINE_HASH,
        "features": FEATURES,
        "cards": CARDS,
        "actions": ACTIONS,
    }
    if any(engine.get(k) != v for k, v in checks.items()):
        raise ValueError("Incompatible engine, observation, card or action contract")
    if type(engine.get("n_cards")) is not int or engine["n_cards"] <= 1:
        raise ValueError("Missing card vocabulary size")
    if info.get("algorithm") != "MaskablePPO":
        raise ValueError("Not a MaskablePPO checkpoint")
    if type(info.get("total_timesteps")) is not int or info["total_timesteps"] < 0:
        raise ValueError("Invalid cumulative training steps")
    if type(info.get("training_seed")) is not int:
        raise ValueError("Invalid training seed")
    try:
        with zipfile.ZipFile(checkpoint) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or not REQUIRED_MEMBERS.issubset(names):
                raise ValueError("Missing/duplicate SB3 policy or optimizer members")
            if archive.testzip() is not None:
                raise ValueError("Corrupt ZIP entry")
    except zipfile.BadZipFile as exc:
        raise ValueError("Invalid SB3 checkpoint archive") from exc
    return {
        "schema": 1,
        "source": str(checkpoint),
        "sha256": actual,
        "size_bytes": size,
        "total_timesteps": info["total_timesteps"],
        "engine": checks,
        "card_vocab_size": engine["n_cards"],
        "archive_and_optimizer_integrity_verified": True,
        "torch_load_verified": False,
        "resumable_training_verified": False,
        "real_game_verified": False,
        "champion_eligible": False,
        "note": "Structural validation only; separately run actual torch load, PPO continuation and full game.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit an already downloaded PPO checkpoint")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = audit_checkpoint(args.checkpoint, args.metadata, args.expected_sha256)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
