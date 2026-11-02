"""Read-only reconciliation of canonical registry, Release digests and legacy inventory.

This is a metadata consistency check, not a binary download, restored PPO run,
full-game receipt, or Champion promotion. It deliberately accepts unequal
inventory coverage because the legacy V5 inventory is a separate historic view.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .registry_integrity import validate_registry

PREFIX = "https://github.com/sstxww/reinforcement-learning/releases/download/"
SHA = re.compile(r"^[0-9a-f]{64}$")


def _index(rows: object, label: str) -> dict:
    if not isinstance(rows, list):
        raise ValueError(f"{label} is not a list")
    indexed = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError(f"{label} contains an invalid row")
        if row["id"] in indexed:
            raise ValueError(f"{label} has duplicate ID {row['id']}")
        indexed[row["id"]] = row
    return indexed


def reconcile(registry: dict, digests: dict, inventory: dict) -> dict:
    """Reject inconsistent same-model claims, but never infer gameplay quality."""
    validate_registry(registry)
    if digests.get("schema") != 1 or inventory.get("schema") != 1:
        raise ValueError("Unsupported release digest or inventory schema")
    candidate = _index(registry["candidates"], "canonical candidates")
    assets = _index(digests.get("assets"), "Release assets")
    legacy = _index(inventory.get("models"), "legacy inventory")
    rows = []
    for model_id, entry in candidate.items():
        if model_id not in assets:
            raise ValueError(f"Canonical model missing Release digest: {model_id}")
        release = assets[model_id]
        weight = release.get("weights")
        meta = release.get("metadata")
        if not isinstance(weight, dict) or not isinstance(meta, dict):
            raise ValueError(f"Missing both Release asset records: {model_id}")
        if weight.get("sha256") != entry["checkpoint_sha256"]:
            raise ValueError(f"Cross-registry model SHA256 mismatch: {model_id}")
        for asset, filename in ((weight, "model.zip"), (meta, "model.metadata.json")):
            if not isinstance(asset.get("sha256"), str) or not SHA.fullmatch(asset["sha256"]):
                raise ValueError(f"Untrusted asset SHA256: {model_id}/{filename}")
            if asset.get("url") != PREFIX + model_id + "/" + filename:
                raise ValueError(f"Untrusted Release URL: {model_id}/{filename}")
        if model_id in legacy:
            if legacy[model_id].get("sha256") != entry["checkpoint_sha256"]:
                raise ValueError(f"Legacy inventory SHA256 mismatch: {model_id}")
            if legacy[model_id].get("url") != weight["url"]:
                raise ValueError(f"Legacy inventory URL mismatch: {model_id}")
        rows.append({
            "model_id": model_id,
            "in_legacy_inventory": model_id in legacy,
            "metadata_digest_indexed": True,
            "weights_download_verified_claim": release.get("weights_bytes_verified") is True,
            "metadata_download_verified_claim": release.get("metadata_bytes_verified") is True,
            "published_release_cpu_load_claim": release.get("model_load_verified") is True,
            "published_release_optimizer_resume_claim": release.get("optimizer_resume_verified") is True,
        })
    latest_id = registry["latest"]["id"]
    latest = next(row for row in rows if row["model_id"] == latest_id)
    safe_to_claim_verified_published_resume = all([
        latest["weights_download_verified_claim"],
        latest["metadata_download_verified_claim"],
        latest["published_release_cpu_load_claim"],
        latest["published_release_optimizer_resume_claim"],
    ])
    return {
        "schema": 1,
        "latest_experimental_unpromoted": latest_id,
        "canonical_candidate_count": len(rows),
        "digest_record_count": len(assets),
        "legacy_inventory_count": len(legacy),
        "legacy_missing_latest": latest_id not in legacy,
        "unindexed_extra_release_ids": sorted(set(assets) - set(candidate)),
        "latest_manifest_resume_gate": safe_to_claim_verified_published_resume,
        "latest_is_champion": False,
        "candidates": rows,
        "warning": ("Metadata-only consistency audit. A true gate would still need "
                    "independent download, SHA256, deserialization, optimizer continuation, "
                    "and model-only full-game tests. Do not train/promote on this output alone."),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    p.add_argument("--digests", type=Path, default=Path("models/release_asset_digests.json"))
    p.add_argument("--inventory", type=Path, default=Path("models/release_inventory_v5.json"))
    p.add_argument("--out", type=Path)
    p.add_argument("--require-latest-manifest-resume", action="store_true")
    a = p.parse_args()
    report = reconcile(*[json.loads(path.read_text(encoding="utf-8"))
                         for path in (a.registry, a.digests, a.inventory)])
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    if a.require_latest_manifest_resume and not report["latest_manifest_resume_gate"]:
        raise SystemExit("Latest published Release has NOT passed independent manifest resume gates")


if __name__ == "__main__":
    main()
