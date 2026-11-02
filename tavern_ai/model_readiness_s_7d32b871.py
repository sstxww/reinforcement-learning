"""Read-only cross-catalog checkpoint readiness gate for V5 (session 7d32b871).

This reports provenance claims without upgrading any unverified claim to a
fresh byte/load/resume check. It deliberately does not mutate model roles.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .registry_integrity import validate_registry
from .release_asset_verifier import validate_asset_index, verify_local

CANONICAL = Path("models/registry.json")
ASSETS = Path("models/release_asset_digests.json")
INVENTORY = Path("models/release_inventory_v5.json")


def audit(canonical: dict, assets: dict, inventory: dict) -> dict:
    canon = validate_registry(canonical)
    cross = validate_asset_index(assets, canonical)
    if not isinstance(inventory, dict) or inventory.get("schema") != 1:
        raise ValueError("Invalid independent inventory")
    inventory_rows = inventory.get("models")
    if not isinstance(inventory_rows, list):
        raise ValueError("Missing independent inventory records")
    by_id = {}
    for row in inventory_rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError("Invalid inventory model")
        if row["id"] in by_id:
            raise ValueError("Duplicate inventory ID")
        by_id[row["id"]] = row
    canonical_rows = {r["id"]: r for r in canonical["candidates"]}
    for ident in set(by_id) & set(canonical_rows):
        if by_id[ident].get("sha256") != canonical_rows[ident]["checkpoint_sha256"]:
            raise ValueError(f"Catalog digest disagreement: {ident}")
    latest = canonical["latest"]
    ident = latest["id"]
    asset = next(a for a in assets["assets"] if a["id"] == ident)
    candidate = canonical_rows[ident]
    checks = {
        "release_asset_digest_index_present": True,
        "historical_weights_bytes_claim": asset["weights_bytes_verified"],
        "historical_metadata_bytes_claim": asset["metadata_bytes_verified"],
        "historical_cpu_load_claim": asset["model_load_verified"],
        "historical_optimizer_resume_claim": asset["optimizer_resume_verified"],
        "canonical_independent_resume_claim":
            candidate.get("independent_optimizer_resume_from_this_release_tested", False)
            if "independent_optimizer_resume_from_this_release_tested" in candidate
            else latest.get("independent_optimizer_resume_from_this_release_tested", False),
        "bytes_reverified_in_this_execution": False,
        "cpu_load_reverified_in_this_execution": False,
        "optimizer_resumed_in_this_execution": False,
        "real_game_in_this_execution": False,
    }
    return {
        "schema": 1,
        "source": "checked-in-catalog-snapshot",
        "canonical_candidate_count": canon["candidates"],
        "asset_index_count": cross["indexed_releases"],
        "independent_inventory_count": len(by_id),
        "independent_inventory_latest_id": inventory.get("roles", {}).get("latest"),
        "canonical_latest_id": ident,
        "model_release_url": latest["release"],
        "expected_sha256": candidate["checkpoint_sha256"],
        "cumulative_steps": candidate["training_steps"],
        "champion": None,
        "checks": checks,
        "automatic_resume_ready": False,
        "champion_eligible": False,
        "decision": "DOWNLOAD_AND_VERIFY_BYTES_LOAD_AND_OPTIMIZER_BEFORE_RESUME",
        "note": (
            "An inventory's null latest is not a verified contradiction: it is an "
            "independent audit catalog. Historical flags are evidence claims, "
            "not fresh checks. No weight was downloaded in this snapshot."
        ),
    }


def cli() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--canonical", type=Path, default=CANONICAL)
    p.add_argument("--assets", type=Path, default=ASSETS)
    p.add_argument("--inventory", type=Path, default=INVENTORY)
    p.add_argument("--weights", type=Path)
    p.add_argument("--metadata", type=Path)
    p.add_argument("--check-load", action="store_true")
    args = p.parse_args()
    if bool(args.weights) != bool(args.metadata):
        p.error("--weights and --metadata must be supplied together")
    if args.check_load and not args.weights:
        p.error("--check-load requires --weights and --metadata")
    canonical = json.loads(args.canonical.read_text(encoding="utf-8"))
    assets = json.loads(args.assets.read_text(encoding="utf-8"))
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    report = audit(canonical, assets, inventory)
    if args.weights:
        result = verify_local(
            assets, canonical, report["canonical_latest_id"],
            args.weights, args.metadata, check_load=args.check_load
        )
        report["checks"]["bytes_reverified_in_this_execution"] = (
            result["weight_bytes_sha256_verified"] and
            result["metadata_bytes_sha256_verified"]
        )
        report["checks"]["cpu_load_reverified_in_this_execution"] = result["sb3_load_checked"]
        report["decision"] = (
            "FRESH_BYTES_AND_LOAD_VERIFIED; OPTIMIZER_RESUME_NOT_TESTED"
            if result["sb3_load_checked"]
            else "FRESH_BYTES_VERIFIED; CPU_LOAD_NOT_TESTED"
        )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    cli()
