"""Fail-closed regression for branch rules and non-cooperating merge writers."""
import pytest
from scripts.v7_main_enforcement_0d5a452fe9 import assess

SHA = "c" * 40


def branch(protected=False):
    return {"name": "main", "commit": {"sha": SHA}, "protected": protected,
            "protection": {"enabled": protected}}


def test_unprotected_main_with_no_rules_is_a_blocker():
    result = assess(branch(), [])
    assert result["verdict"] == "BLOCKED_UNPROTECTED_MAIN"
    assert result["branch_protected"] is False
    assert result["main_sha"] == SHA
    assert result["globally_exclusive_merge_permission"] is False


def test_cooperative_mutex_is_not_global_authorization():
    # Even a protected branch with an active ruleset cannot prove all writers
    # use a single enforced merge queue without reviewing bypass permissions.
    result = assess(branch(True), [{"id": 123, "enforcement": "active"}])
    assert result["verdict"] == "BLOCKED_EXCLUSIVITY_NOT_PROVEN"
    assert result["active_ruleset_ids"] == [123]
    assert result["globally_exclusive_merge_permission"] is False


def test_rule_presence_without_protection_needs_manual_review():
    result = assess(branch(False), [{"id": 2, "enforcement": "active"}])
    assert result["verdict"] == "BLOCKED_EXCLUSIVITY_NOT_PROVEN"
    assert result["globally_exclusive_merge_permission"] is False


@pytest.mark.parametrize("bad", [
    {"name": "develop", "commit": {"sha": SHA}, "protected": False},
    {"name": "main", "commit": {"sha": "short"}, "protected": False},
    {"name": "main", "commit": {}, "protected": False},
    {"name": "main", "commit": {"sha": SHA}},
])
def test_bad_branch_input_fails_closed(bad):
    with pytest.raises(ValueError):
        assess(bad, [])


@pytest.mark.parametrize("bad_rulesets", [None, {}, "active"])
def test_malformed_rulesets_fail_closed(bad_rulesets):
    with pytest.raises(ValueError):
        assess(branch(), bad_rulesets)
