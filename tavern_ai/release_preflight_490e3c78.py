"""Read-only Release checkpoint archive+metadata preflight.

Builds on the mainline model registry validator, never deserializes pickle,
performs gradient updates, or claims successful policy inference/continuation.
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from .registry_integrity import validate_registry, verify_checkpoint


def verify_release_pair(registry: dict, model_id: str, checkpoint: Path,
                        metadata: Path) -> dict:
    """Verify actual downloaded bytes against a registered model's immutable record."""
    validate_registry(registry)
    rows = [row for row in registry["candidates"] if row["id"] == model_id]
    if len(rows) != 1:
        raise ValueError("Unknown or ambiguous model ID")
    row = rows[0]
    digest = verify_checkpoint(checkpoint, row["checkpoint_sha256"])
    if not zipfile.is_zipfile(checkpoint):
        raise ValueError("Checkpoint is not a ZIP archive")
    with zipfile.ZipFile(checkpoint) as archive:
        members = archive.infolist()
        if len(members) > 1000 or sum(z.file_size for z in members) > 512 * 1024 * 1024:
            raise ValueError("Archive size or members exceed safe preflight budget")
        names = {z.filename for z in members}
        required = {"data", "policy.pth", "policy.optimizer.pth"}
        if not required.issubset(names):
            raise ValueError("Checkpoint missing SB3 policy or optimizer state entry")
        if archive.testzip() is not None:
            raise ValueError("Checkpoint contains corrupt ZIP member")
    info = json.loads(metadata.read_text(encoding="utf-8"))
    engine = info.get("engine")
    if not isinstance(engine, dict):
        raise ValueError("Missing metadata engine")
    expected = registry["engine"]
    if (engine.get("version"), engine.get("source_hash"),
            engine.get("features"), engine.get("cards"), engine.get("actions")) != (
            expected["version"], expected["source_hash"],
            expected["float_features"], expected["card_slots"],
            expected["action_count"]):
        raise ValueError("Checkpoint metadata/registry engine mismatch")
    if type(info.get("total_timesteps")) is not int or info["total_timesteps"] != row["training_steps"]:
        raise ValueError("Checkpoint train steps mismatch")
    if info.get("checkpoint_sha256") not in (None, digest):
        raise ValueError("Checkpoint metadata SHA256 mismatch")
    if info.get("algorithm") not in (None, "MaskablePPO"):
        raise ValueError("Unexpected model algorithm")
    compat = info.get("compatibility")
    if compat is not None and compat.get("engine") != engine:
        raise ValueError("Checkpoint compatibility manifest disagrees with metadata")
    return {
        "model_id": model_id,
        "sha256_verified": digest,
        "zip_crc_verified": True,
        "policy_archive_entry_present": True,
        "optimizer_archive_entry_present": True,
        "registry_metadata_steps_consistent": True,
        "torch_model_loaded": False,
        "optimizer_restored": False,
        "ppo_steps_executed": 0,
        "full_game_completed_by_this_check": False,
        "champion_promoted": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    p.add_argument("--model-id", required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--metadata", type=Path, required=True)
    a = p.parse_args()
    data = json.loads(a.registry.read_text(encoding="utf-8"))
    print(json.dumps(verify_release_pair(data, a.model_id, a.model, a.metadata),
                     sort_keys=True))


if __name__ == "__main__":
    main()
