"""Fail-closed checkpoint selection for main incremental PPO training.

A workflow Artifact is temporary and its in-band metadata SHA is a corruption
check, not independent provenance. A Release must ALSO be verified against the
canonical out-of-band digest index before passing this gate. This gate does not
prove model performance, successful optimizer continuation, or Champion status.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .checkpoint_preflight import audit_archive

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def inspect_continuation(
    checkpoint: Path,
    metadata: Path,
    *,
    allow_fresh_start: bool = False,
    expected_sha256: str | None = None,
) -> dict:
    """Return a safe explicit mode, or refuse missing/incompatible checkpoints.

    The in-band metadata digest only detects corruption; the caller must
    independently verify Release asset bytes for trusted model provenance.
    """
    checkpoint, metadata = Path(checkpoint), Path(metadata)
    have_weights, have_metadata = checkpoint.is_file(), metadata.is_file()
    if have_weights != have_metadata:
        raise ValueError("Incomplete checkpoint pair; refusing silent fresh start")
    if not have_weights:
        if not allow_fresh_start:
            raise ValueError("No resumable checkpoint; explicit fresh-start opt-in required")
        return {
            "mode": "fresh_explicit",
            "checkpoint_verified": False,
            "model_strength_verified": False,
        }
    try:
        obj = json.loads(metadata.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError("Unreadable checkpoint metadata") from exc
    if not isinstance(obj, dict):
        raise ValueError("Checkpoint metadata must be a JSON object")
    embedded = obj.get("checkpoint_sha256")
    if not isinstance(embedded, str) or not _SHA256.fullmatch(embedded):
        raise ValueError("Checkpoint has no recorded SHA256; refuse legacy unverified resume")
    if expected_sha256 is not None:
        if not _SHA256.fullmatch(expected_sha256) or expected_sha256 != embedded:
            raise ValueError("Trusted Release SHA256 conflicts with checkpoint metadata")
    report = audit_archive(checkpoint, metadata, expected_sha256 or embedded)
    return {
        "mode": "resume_verified_archive",
        "checkpoint_sha256": embedded,
        "total_timesteps": report["total_timesteps"],
        "metadata_schema": report["checkpoint_metadata_schema"],
        "archive_integrity": report["archive_integrity"],
        "provenance_out_of_band": expected_sha256 is not None,
        "optimizer_resume_verified": False,
        "model_strength_verified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--allow-fresh-start", action="store_true")
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    result = inspect_continuation(
        args.checkpoint, args.metadata,
        allow_fresh_start=args.allow_fresh_start,
        expected_sha256=args.expected_sha256,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
