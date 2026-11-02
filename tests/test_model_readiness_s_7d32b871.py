"""Offline, synthetic-mutation and checked-in-manifest readiness regressions."""
import copy
import json
from pathlib import Path

import pytest

from tavern_ai.model_readiness_s_7d32b871 import audit

ROOT = Path(__file__).resolve().parents[1]


def documents():
    return tuple(
        json.loads((ROOT / p).read_text(encoding="utf-8"))
        for p in (
            "models/registry.json",
            "models/release_asset_digests.json",
            "models/release_inventory_v5.json",
        )
    )


def test_checked_in_latest_is_not_auto_resumable_or_champion():
    canonical, assets, inventory = documents()
    report = audit(canonical, assets, inventory)
    assert report["canonical_latest_id"] == canonical["latest"]["id"]
    assert report["expected_sha256"] == canonical["latest"]["checkpoint_sha256"]
    assert report["cumulative_steps"] == canonical["latest"]["training_steps"]
    assert report["champion"] is None
    assert report["automatic_resume_ready"] is False
    assert report["checks"]["bytes_reverified_in_this_execution"] is False
    assert report["checks"]["optimizer_resumed_in_this_execution"] is False


def test_rejects_drift_between_canonical_and_independent_inventory():
    canonical, assets, inventory = documents()
    id_ = inventory["models"][0]["id"]
    assert id_ in {m["id"] for m in canonical["candidates"]}
    for row in inventory["models"]:
        if row["id"] == id_:
            row["sha256"] = "a" * 64
            break
    with pytest.raises(ValueError, match="digest disagreement"):
        audit(canonical, assets, inventory)


def test_rejects_drift_between_canonical_and_release_assets():
    canonical, assets, inventory = documents()
    target = canonical["latest"]["id"]
    for row in assets["assets"]:
        if row["id"] == target:
            row["weights"]["sha256"] = "f" * 64
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        audit(canonical, assets, inventory)


def test_rejects_fake_champion():
    canonical, assets, inventory = documents()
    canonical["champion"] = canonical["latest"]["id"]
    with pytest.raises(ValueError, match="champion|promotion"):
        audit(canonical, assets, inventory)


def test_rejects_duplicate_audit_inventory_entry():
    canonical, assets, inventory = documents()
    inventory["models"].append(copy.deepcopy(inventory["models"][0]))
    with pytest.raises(ValueError, match="Duplicate inventory"):
        audit(canonical, assets, inventory)


def test_historical_claim_flags_never_imply_fresh_verification():
    canonical, assets, inventory = documents()
    for r in assets["assets"]:
        r["weights_bytes_verified"] = True
        r["metadata_bytes_verified"] = True
        r["model_load_verified"] = True
        # Never claim test happened locally without actual bytes.
    result = audit(canonical, assets, inventory)
    assert result["checks"]["historical_cpu_load_claim"] is True
    assert result["checks"]["cpu_load_reverified_in_this_execution"] is False
    assert result["automatic_resume_ready"] is False
