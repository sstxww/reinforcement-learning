"""Staged checkpoint writes and checksum-bound resume for incremental PPO.

Saving a ZIP and its metadata is not a single filesystem transaction. If a
crash occurs between replacements, the next verified resume fails closed.
Legacy checkpoint metadata without a digest must be preflighted independently.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_resume_digest(path: Path, metadata: dict) -> bool:
    """Verify a bound SHA; False means legacy metadata requires outside audit."""
    expected = metadata.get("checkpoint_sha256")
    if expected is None:
        return False
    if not isinstance(expected, str) or not _SHA256.fullmatch(expected):
        raise ValueError("Invalid checkpoint_sha256 in resume metadata")
    if sha256_file(path) != expected:
        raise ValueError("Checkpoint SHA256 mismatch; refusing resume")
    return True


def save_checkpoint(model: object, model_path: Path, metadata: dict) -> dict:
    """Stage checkpoint and bound metadata; never write the target mid-save."""
    model_path = Path(model_path)
    if model_path.suffix != ".zip":
        raise ValueError("Checkpoint path must have a .zip suffix")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = model_path.with_suffix(".metadata.json")
    fd, tmp_zip = tempfile.mkstemp(prefix=".checkpoint-", suffix=".zip", dir=model_path.parent)
    os.close(fd)
    fd, tmp_meta = tempfile.mkstemp(prefix=".checkpoint-", suffix=".json", dir=model_path.parent)
    os.close(fd)
    try:
        model.save(str(tmp_zip))
        if not Path(tmp_zip).is_file() or Path(tmp_zip).stat().st_size == 0:
            raise ValueError("Training library wrote an empty checkpoint")
        saved = {**metadata, "checkpoint_sha256": sha256_file(Path(tmp_zip))}
        Path(tmp_meta).write_text(json.dumps(saved, indent=2, ensure_ascii=False), encoding="utf-8")
        # Committing ZIP first leaves a detectably mismatched old metadata
        # if power fails before the second replace. A later resume refuses.
        os.replace(tmp_zip, model_path)
        os.replace(tmp_meta, metadata_path)
        return saved
    finally:
        Path(tmp_zip).unlink(missing_ok=True)
        Path(tmp_meta).unlink(missing_ok=True)
