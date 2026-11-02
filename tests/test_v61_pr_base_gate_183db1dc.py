"""Synthetic P0 premerge checks, not real-game evidence."""
from __future__ import annotations

import copy
import pytest

from scripts.v61_pr_base_gate_183db1dc import audit

MAIN = "a" * 40
HEAD = "b" * 40


def valid_pr():
    return {
        "number": 999, "state": "open", "draft": False,
        "mergeable": True,
        "base": {"ref": "main", "sha": MAIN},
        "head": {"ref": "agent/session/task", "sha": HEAD},
    }


def checks():
    return {"check_runs": [
        {"head_sha": HEAD, "name": "tests-and-full-match",
         "status": "completed", "conclusion": "success"}
    ]}


def test_positive_gate_is_still_human_only():
    r = audit(valid_pr(), MAIN, checks(), dependencies_cleared=True)
    assert r["decision"] == "eligible_for_integrator_review"
    assert r["auto_merge_authorized"] is False


def test_nonmain_target_blocked_even_if_ci_green():
    p = valid_pr()
    p["base"]["ref"] = "agent/learning/v1"
    r = audit(p, MAIN, checks(), dependencies_cleared=True)
    assert "PR targets a non-main dependency branch" in r["blockers"]


def test_stale_main_sha_blocked():
    p = valid_pr()
    p["base"]["sha"] = "f" * 40
    assert "PR base SHA differs from current main" in audit(
        p, MAIN, checks(), dependencies_cleared=True)["blockers"]


@pytest.mark.parametrize("field,value", [
    ("draft", True), ("draft", None),
    ("mergeable", False), ("mergeable", None),
    ("state", "closed"),
])
def test_fail_closed_metadata(field, value):
    p = valid_pr()
    p[field] = value
    assert audit(p, MAIN, checks(), dependencies_cleared=True)["blockers"]


def test_missing_required_current_head_check_is_blocked():
    c = checks()
    c["check_runs"][0]["head_sha"] = "c" * 40
    assert "Required latest-head full-match CI not successful" in audit(
        valid_pr(), MAIN, c, dependencies_cleared=True)["blockers"]


def test_failed_or_pending_checks_block():
    for status, conclusion in [("in_progress", None), ("completed", "failure")]:
        c = checks()
        c["check_runs"][0]["status"] = status
        c["check_runs"][0]["conclusion"] = conclusion
        assert "Latest-head checks are pending or unsuccessful" in audit(
            valid_pr(), MAIN, c, dependencies_cleared=True)["blockers"]


def test_no_implicit_dependency_approval():
    r = audit(valid_pr(), MAIN, checks())
    assert "Human dependency/receipt review is not confirmed" in r["blockers"]


def test_invalid_main_sha_is_error():
    with pytest.raises(ValueError, match="Current main SHA"):
        audit(valid_pr(), "short", checks(), dependencies_cleared=True)


def test_unknown_check_payload_fail_closed():
    assert "Latest-head CI checks are unavailable" in audit(
        valid_pr(), MAIN, {}, dependencies_cleared=True)["blockers"]
