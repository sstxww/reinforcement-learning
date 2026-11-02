"""Explicit, fail-closed Release selection for bounded main PPO continuation.

This does not promote a model or certify competitive improvement. The operator
must supply a registered immutable tag; locally downloaded bytes are checked
before the existing training entry point loads or continues them.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .registry_integrity import validate_registry
from .checkpoint_preflight import audit_archive

_TAG = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


def gate(registry_path: Path, tag: str, model: Path | None = None,
         metadata: Path | None = None) -> dict:
    if not isinstance(tag, str) or not _TAG.fullmatch(tag):
        raise ValueError("Unsafe or missing immutable Release tag")
    data = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    validate_registry(data)
    matches = [row for row in data["candidates"] if row["id"] == tag]
    if len(matches) != 1:
        raise ValueError("Tag is not an explicitly registered candidate")
    row = matches[0]
    if row.get("role") != "candidate_unpromoted":
        raise ValueError("Only unpromoted experimental candidates may be resumed")
    result = {
        "release_tag": tag,
        "expected_sha256": row["checkpoint_sha256"],
        "parent_training_steps": row["training_steps"],
        "registry_checked": True,
        "downloaded_bytes_verified": False,
        "champion_promoted": False,
    }
    if (model is None) != (metadata is None):
        raise ValueError("Supply both downloaded model and its metadata")
    if model is not None:
        receipt = audit_archive(Path(model), Path(metadata),
                                row["checkpoint_sha256"])
        if receipt["total_timesteps"] != row["training_steps"]:
            raise ValueError("Release and registry training step mismatch")
        result["downloaded_bytes_verified"] = True
        result["archive_integrity"] = receipt["archive_integrity"]
        result["cpu_load"] = "pending_training_entrypoint"
        result["optimizer_resume"] = "pending_training_entrypoint"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--tag", required=True)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()
    print(json.dumps(gate(args.registry, args.tag, args.model, args.metadata),
                     sort_keys=True))


if __name__ == "__main__":
    main()
