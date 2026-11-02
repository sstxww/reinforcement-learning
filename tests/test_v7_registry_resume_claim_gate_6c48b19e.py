"""Offline tests for V7 Release-specific provenance audit, no fake game receipts."""
import copy
import json
from pathlib import Path

import pytest

from scripts.v7_registry_resume_claim_gate_6c48b19e import audit_registry


ROOT = Path(__file__).resolve().parents[1]


def live():
    return json.loads((ROOT / "models/registry.json").read_text(encoding="utf-8"))


def test_current_registry_historical_claim_cannot_override_specific_false():
    report = audit_registry(live())
    assert report["main_registry_latest_id"] == "v5-s-20261102-68099929-1408-41428692617"
    assert report["historical_latest_release_resume_claim"] is True
    assert report["historical_vs_specific_claim_requires_review"] is True
    assert "independent_optimizer_resume_from_this_release_tested" in report["unmet_per_release_claims"]
    assert not report["release_ready_for_automatic_training_by_this_audit"]


def test_all_manifest_claims_true_still_not_independent_proof():
    doc = copy.deepcopy(live())
    for key in ("release_download_sha256_verified",
                "model_load_from_downloaded_release_tested",
                "independent_optimizer_resume_from_this_release_tested"):
        doc["latest"][key] = True
    result = audit_registry(doc)
    assert result["per_release_manifest_flags_complete"]
    assert not result["checkpoint_bytes_downloaded_by_this_audit"]
    assert not result["optimizer_state_loaded_by_this_audit"]
    assert result["new_ppo_steps_by_this_audit"] == 0
    assert not result["release_ready_for_automatic_training_by_this_audit"]


@pytest.mark.parametrize("value", [1, "true", [], {}])
def test_boolean_claims_are_exact(value):
    doc = copy.deepcopy(live())
    doc["latest"]["model_load_from_downloaded_release_tested"] = value
    with pytest.raises(ValueError, match="Non-boolean"):
        audit_registry(doc)


def test_registry_identity_sha_mismatch_fails_closed():
    doc = copy.deepcopy(live())
    doc["latest"]["checkpoint_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="provenance"):
        audit_registry(doc)


def test_no_unreviewed_champion_promotion():
    doc = copy.deepcopy(live())
    doc["champion"] = doc["latest"]["id"]
    with pytest.raises(ValueError, match="champion"):
        audit_registry(doc)


def test_missing_model_specific_flag_does_not_become_true():
    doc = copy.deepcopy(live())
    doc["latest"].pop("independent_optimizer_resume_from_this_release_tested", None)
    result = audit_registry(doc)
    assert result["per_release_claims"]["independent_optimizer_resume_from_this_release_tested"] is None
    assert result["historical_vs_specific_claim_requires_review"]
    assert not result["per_release_manifest_flags_complete"]
