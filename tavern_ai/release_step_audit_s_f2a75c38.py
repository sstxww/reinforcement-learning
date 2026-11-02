"""Legacy Release-inventory CPU-load step provenance check (V7, read-only).

This closes a narrow gap in the older models/release_inventory_v5.json path:
a ZIP and its metadata may agree yet the actual loaded SB3 checkpoint can
carry a different cumulative num_timesteps. No resume or strength is inferred.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .model_registry import read_registry, verify_local


def require_loaded_steps(actual: object, metadata_steps: object, catalog_steps: object = None) -> int:
    """Reject fabricated, missing, stale, and boolean SB3 step counters."""
    if type(metadata_steps) is not int or metadata_steps < 1:
        raise ValueError("Invalid metadata training step counter")
    if catalog_steps is not None and (
        type(catalog_steps) is not int or catalog_steps != metadata_steps
    ):
        raise ValueError("Catalog/metadata training steps mismatch")
    if type(actual) is not int or actual != metadata_steps:
        raise ValueError("Loaded SB3 num_timesteps does not match metadata")
    return actual


def audit(entry: dict, archive: Path, metadata: Path) -> dict:
    """Verify bytes, optimizer archive, CPU load/layout and actual SB3 step lineage."""
    checked = verify_local(entry, archive, metadata, load=True)
    from sb3_contrib import MaskablePPO
    loaded = MaskablePPO.load(str(archive), device="cpu")
    doc = json.loads(metadata.read_text(encoding="utf-8"))
    steps = require_loaded_steps(
        getattr(loaded, "num_timesteps", None),
        doc.get("total_timesteps"),
        entry.get("reported_total_timesteps"),
    )
    return {
        "model_id": entry["id"],
        "checkpoint_sha256": checked["sha256"],
        "metadata_steps": steps,
        "sb3_loaded_steps": steps,
        "cpu_load_and_layout_checked": True,
        "loaded_step_lineage_verified": True,
        "optimizer_state_present": checked["optimizer_state_present"],
        "optimizer_resume_verified": False,
        "full_eight_seat_game_verified": False,
        "competitive_gain_verified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=Path("models/release_inventory_v5.json"))
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()
    inventory = read_registry(args.inventory)
    item = next((row for row in inventory["models"] if row["id"] == args.model_id), None)
    if item is None:
        parser.error("Unknown immutable model ID")
    print(json.dumps(audit(item, args.checkpoint, args.metadata), sort_keys=True))


if __name__ == "__main__":
    main()
