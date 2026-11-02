"""Conservative scheduled-training resume gate.

Prevents an expired/missing Actions Artifact from silently resetting PPO to
random weights. Archive checks validate local integrity, not trusted lineage.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import zipfile
from pathlib import Path

from .contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES

_MAX_ZIP_BYTES = 512 * 1024 * 1024
_REQUIRED_ZIP_FILES = {"data", "policy.pth", "policy.optimizer.pth"}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def decide_resume(checkpoint: Path, metadata: Path, *, allow_fresh: bool = False) -> dict:
    """Return an explicit resume/fresh decision or fail without touching files."""
    checkpoint, metadata = Path(checkpoint), Path(metadata)
    has_checkpoint, has_metadata = checkpoint.is_file(), metadata.is_file()
    if has_checkpoint != has_metadata:
        raise ValueError("Incomplete checkpoint pair; refusing resume or fresh start")
    if not has_checkpoint:
        if not allow_fresh:
            raise ValueError(
                "No resumable checkpoint; refusing silent random initialization. "
                "Recover verified Release assets or explicitly authorize a fresh start."
            )
        return {"mode": "fresh", "explicitly_authorized": True,
                "persistent_checkpoint_verified": False}

    if checkpoint.stat().st_size == 0 or checkpoint.stat().st_size > _MAX_ZIP_BYTES:
        raise ValueError("Checkpoint archive outside safe size bounds")
    try:
        info = json.loads(metadata.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid checkpoint metadata JSON") from exc
    if not isinstance(info, dict) or type(info.get("schema")) is not int or info["schema"] not in (1, 2):
        raise ValueError("Unsupported checkpoint metadata schema")
    if info.get("algorithm") != "MaskablePPO":
        raise ValueError("Unsupported checkpoint algorithm")
    if type(info.get("total_timesteps")) is not int or info["total_timesteps"] <= 0:
        raise ValueError("Missing cumulative PPO training steps")
    engine = info.get("engine")
    expected = {"version": "1.1.0", "source_hash": ENGINE_HASH,
                "features": FEATURES, "cards": CARDS, "actions": ACTIONS}
    if not isinstance(engine, dict) or any(
        type(engine.get(key)) is not type(value) or engine.get(key) != value
        for key, value in expected.items()
    ):
        raise ValueError("Checkpoint does not match pinned TavernGym contract")
    try:
        with zipfile.ZipFile(checkpoint) as archive:
            members = archive.infolist()
            names = [member.filename for member in members]
            if (len(names) > 64 or len(set(names)) != len(names)
                    or not _REQUIRED_ZIP_FILES.issubset(set(names))):
                raise ValueError("Incomplete or duplicate PPO archive entries")
            if any(name.startswith("/") or ".." in Path(name).parts for name in names):
                raise ValueError("Unsafe archive path")
            if sum(m.file_size for m in members) > _MAX_ZIP_BYTES:
                raise ValueError("Checkpoint ZIP expands beyond safety limit")
            if archive.testzip() is not None:
                raise ValueError("Checkpoint ZIP CRC failure")
    except (OSError, zipfile.BadZipFile, EOFError) as exc:
        raise ValueError("Corrupt PPO archive") from exc
    recorded = info.get("checkpoint_sha256")
    checked = False
    if recorded is not None:
        if not isinstance(recorded, str) or not _HEX64.fullmatch(recorded):
            raise ValueError("Malformed checkpoint SHA256 in metadata")
        digest = hashlib.sha256()
        with checkpoint.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        if not hmac.compare_digest(digest.hexdigest(), recorded):
            raise ValueError("Model bytes differ from checkpoint metadata SHA256")
        checked = True
    return {
        "mode": "resume", "total_timesteps": info["total_timesteps"],
        "paired_files_present": True, "local_metadata_digest_matched": checked,
        "external_release_provenance_verified": False,
        "note": "Local checks do not replace a trusted Release SHA or live optimizer resume.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--allow-fresh-start", action="store_true")
    args = parser.parse_args()
    result = decide_resume(args.checkpoint, args.metadata, allow_fresh=args.allow_fresh_start)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
