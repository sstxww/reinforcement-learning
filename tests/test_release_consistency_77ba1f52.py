"""Regressions for canonical/digest/legacy model lineage reconciliation."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tavern_ai.release_consistency_77ba1f52 import reconcile

ROOT = Path(__file__).resolve().parents[1]


def fixtures():
    return tuple(json.loads((ROOT / "models" / name).read_text(encoding="utf-8"))
                 for name in ("registry.json", "release_asset_digests.json",
                              "release_inventory_v5.json"))


def test_real_main_index_consistency_is_dynamic():
    registry, digests, inventory = fixtures()
    report = reconcile(registry, digests, inventory)
    assert report["canonical_candidate_count"] == len(registry["candidates"])
    assert report["latest_experimental_unpromoted"] == registry["latest"]["id"]
    assert report["latest_is_champion"] is False
    assert all(x["metadata_digest_indexed"] for x in report["candidates"])


def test_tampered_weight_digest_is_a_hard_failure():
    reg, digests, inv = fixtures()
    latest = reg["latest"]["id"]
    row = next(r for r in digests["assets"] if r["id"] == latest)
    row["weights"]["sha256"] = "a" * 64
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        reconcile(reg, digests, inv)


def test_missing_latest_digest_is_a_hard_failure():
    reg, digests, inv = fixtures()
    latest = reg["latest"]["id"]
    digests["assets"] = [r for r in digests["assets"] if r["id"] != latest]
    with pytest.raises(ValueError, match="missing Release digest"):
        reconcile(reg, digests, inv)


def test_duplicate_digest_rejected():
    reg, digests, inv = fixtures()
    digests["assets"].append(copy.deepcopy(digests["assets"][0]))
    with pytest.raises(ValueError, match="duplicate ID"):
        reconcile(reg, digests, inv)


def test_legacy_partial_coverage_is_not_false_strength_signal():
    reg, digests, inv = fixtures()
    inv["models"] = []
    report = reconcile(reg, digests, inv)
    assert report["legacy_missing_latest"] is True
    assert report["latest_is_champion"] is False


def test_claimed_resume_requires_model_load_and_optimizer():
    reg, digests, inv = fixtures()
    latest = reg["latest"]["id"]
    row = next(x for x in digests["assets"] if x["id"] == latest)
    row["weights_bytes_verified"] = True
    row["metadata_bytes_verified"] = True
    row["model_load_verified"] = False
    row["optimizer_resume_verified"] = False
    report = reconcile(reg, digests, inv)
    assert report["latest_manifest_resume_gate"] is False
    row["model_load_verified"] = True
    row["optimizer_resume_verified"] = True
    assert reconcile(reg, digests, inv)["latest_manifest_resume_gate"] is True
