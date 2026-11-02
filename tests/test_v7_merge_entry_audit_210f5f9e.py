"""Synthetic merge preflight failures; not TavernGym games or trained models."""
import pytest
from tavern_ai.v7_merge_entry_audit_210f5f9e import audit

SHA = "c1b828734527bae6141805581693d890cc3bff94"


def observed_branch():
    return {"name": "main", "commit": {"sha": SHA}, "protected": False,
            "protection": {"enabled": False, "required_status_checks": {
                "enforcement_level": "off", "checks": [], "contexts": []}}}


def test_live_unprotected_branch_must_block():
    r = audit(observed_branch(), [])
    assert r["eligible_for_exclusive_merge"] is False
    assert r["observed_main_sha"] == SHA
    assert "not protected" in " ".join(r["blockers"])


def test_stale_main_must_block():
    assert "Main advanced" in " ".join(
        audit(observed_branch(), [], "a" * 40)["blockers"])


def test_bad_branch_identity_must_block():
    b = observed_branch()
    b["commit"]["sha"] = ""
    assert "Missing verifiable" in " ".join(audit(b, [])["blockers"])


def test_status_checks_without_protection_do_not_grant_lock():
    b = observed_branch()
    b["protection"]["required_status_checks"] = {
        "enforcement_level": "on", "checks": [{"context": "CI"}]}
    assert audit(b, [])["eligible_for_exclusive_merge"] is False


def test_queue_without_proof_all_writers_use_it_still_blocks():
    b = observed_branch()
    b["protected"] = True
    b["protection"] = {"enabled": True, "required_status_checks": {
        "enforcement_level": "on", "checks": [{"context": "CI"}]}}
    q = {"target": "branch", "enforcement": "active",
         "conditions": {"ref_name": {"include": ["refs/heads/main"]}},
         "rules": [{"type": "merge_queue"}]}
    r = audit(b, [q])
    assert r["eligible_for_exclusive_merge"] is False
    assert r["blockers"] == [
        "All concurrent merge writers have not proven exclusive routing"]


def test_unrelated_queue_is_not_main_queue():
    q = {"target": "branch", "enforcement": "active",
         "conditions": {"ref_name": {"include": ["refs/heads/dev"]}},
         "rules": [{"type": "merge_queue"}]}
    assert "No active main-scoped" in " ".join(
        audit(observed_branch(), [q])["blockers"])


@pytest.mark.parametrize("branch,rulesets", [([], []), (observed_branch(), None)])
def test_malformed_api_shapes_rejected(branch, rulesets):
    with pytest.raises(ValueError):
        audit(branch, rulesets)
