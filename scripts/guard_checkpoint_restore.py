"""Fail-closed, read-only compatibility check for a resumed PPO checkpoint.

Checks a local artifact *before* MaskablePPO deserialization. A metadata-carried
hash is not an independently trusted digest. Supply --expected-sha256 when
there is an external, immutable Release/registry digest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES

_HEX = re.compile(r"[0-9a-f]{64}\Z")
_REQUIRED_ZIP = {"data", "policy.pth", "policy.optimizer.pth"}
_MAX_UNCOMPRESSED = 1_000_000_000


def verify(model_path: Path, metadata_path: Path, expected_sha256: str | None = None) -> dict:
    if not model_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError("Both checkpoint and its metadata must exist")
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(meta, dict) or type(meta.get("schema")) is not int or meta["schema"] not in (1, 2):
        raise ValueError("Unsupported metadata schema")
    if meta.get("algorithm") != "MaskablePPO":
        raise ValueError("Unexpected checkpoint algorithm")
    if type(meta.get("total_timesteps")) is not int or meta["total_timesteps"] < 1:
        raise ValueError("Missing positive cumulative steps")
    engine = meta.get("engine")
    expected = {"version": "1.1.0", "source_hash": ENGINE_HASH,
                "features": FEATURES, "cards": CARDS, "actions": ACTIONS}
    if not isinstance(engine, dict) or any(engine.get(k) != v for k, v in expected.items()):
        raise ValueError("Incompatible pinned TavernGym contract")
    if meta["schema"] == 2:
        compat = meta.get("compatibility")
        if not isinstance(compat, dict) or compat.get("engine") != engine:
            raise ValueError("Incompatible schema-2 compatibility engine")

    digest = hashlib.sha256()
    with model_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    for source, claimed in (("external expected digest", expected_sha256),
                            ("checkpoint metadata digest", meta.get("checkpoint_sha256"))):
        if claimed is None:
            continue
        if not isinstance(claimed, str) or not _HEX.fullmatch(claimed) or actual != claimed:
            raise ValueError(f"Invalid or mismatched {source}")
    try:
        with zipfile.ZipFile(model_path, "r") as archive:
            info = archive.infolist()
            if len(info) > 1000 or sum(z.file_size for z in info) > _MAX_UNCOMPRESSED:
                raise ValueError("Checkpoint ZIP exceeds resource limit")
            if not _REQUIRED_ZIP.issubset(archive.namelist()):
                raise ValueError("Checkpoint is missing PPO optimizer or policy state")
            if (bad := archive.testzip()) is not None:
                raise ValueError(f"Checkpoint ZIP CRC mismatch in {bad}")
    except zipfile.BadZipFile as exc:
        raise ValueError("Invalid checkpoint ZIP archive") from exc

    return {"cumulative_steps": meta["total_timesteps"],
            "sha256": actual, "zip_crc_verified": True,
            "metadata_engine_verified": True,
            "external_sha256_verified": expected_sha256 is not None,
            "model_deserialized": False, "optimizer_resume_tested": False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--expected-sha256")
    a = p.parse_args()
    print(json.dumps(verify(a.model, a.metadata, a.expected_sha256), sort_keys=True))


if __name__ == "__main__":
    main()
