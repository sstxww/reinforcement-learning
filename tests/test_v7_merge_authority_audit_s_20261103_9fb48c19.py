"""V7 concurrency-safety regressions: synthetic API records, never real merges."""
from __future__ import annotations

import copy
import subprocess

import pytest

from scripts import v7_merge_authority_audit_s_20261103_9fb48c19 as subject

MAIN = "c1b828734527bae6141805581693d890cc3bff94"
HEAD = "8f4be75cba8463a3f0a74f0e0b72a027a0bad8b5"


def sample():
    return {
        "main": {"sha": MAIN, "protected": False},
        "pr": {"head_sha": HEAD, "base": "main", "state": "open",
               "draft": False, "mergeable": True},
        "pr_runs": [{"id": 41511418837, "head_sha": HEAD,
                     "event": "pull_request", "status": "completed",
                     "conclusion": "success"}],
        "rulesets": [],
        "coordination_claim": {
            "state": "held", "owner": "another-session", "lease_valid": True
        },
    }


def test_real_incident_shape_blocks_unprotected_main_even_with_cas_lease():
    result = subject.audit(sample())
    assert result["merge_authorized"] is False
    assert "main_not_protected" in result["problems"]
    assert "exclusive_merge_writer_authority_not_proven" in result["problems"]


def test_stale_ci_from_old_pr_head_is_not_accepted():
    data = sample()
    data["pr_runs"][0]["head_sha"] = "0" * 40
    assert "no_successful_exact_head_pr_ci" in subject.audit(data)["problems"]


def test_in_progress_or_failed_check_cannot_count_as_green():
    for status, conclusion in (("in_progress", None), ("completed", "failure")):
        data = sample()
        data["pr_runs"][0].update(status=status, conclusion=conclusion)
        assert "no_successful_exact_head_pr_ci" in subject.audit(data)["problems"]


def test_queue_metadata_is_not_equivalent_to_global_authority():
    data = sample()
    data["main"]["protected"] = True
    data["rulesets"] = [{"enforcement": "active", "bypass_actors": [],
                        "rules": [{"type": "merge_queue"}]}]
    result = subject.audit(data)
    assert result["active_queue_ruleset_observed"] is True
    assert result["merge_authorized"] is False
    assert result["problems"] == ["exclusive_merge_writer_authority_not_proven"]


def test_bypass_or_evaluation_mode_ruleset_does_not_count():
    for change in ({"bypass_actors": [{"actor_id": 1}]},
                   {"enforcement": "evaluate"}):
        data = sample()
        data["main"]["protected"] = True
        rules = {"enforcement": "active", "bypass_actors": [],
                 "rules": [{"type": "merge_queue"}]}
        rules.update(change)
        data["rulesets"] = [rules]
        assert not subject.audit(data)["active_queue_ruleset_observed"]


def test_draft_wrong_base_missing_sha_all_fail_closed():
    data = sample()
    data["pr"].update(draft=True, base="agent/foo", head_sha="invalid")
    result = subject.audit(data)
    assert {"draft_pr", "wrong_pr_target_or_state",
            "pr_head_sha_unverified"}.issubset(set(result["problems"]))
    assert result["merge_authorized"] is False


def test_live_probe_uses_get_only_and_exact_pr_head(monkeypatch):
    calls = []

    def fake_get(path):
        calls.append(path)
        if path.endswith("/branches/main"):
            return {"commit": {"sha": MAIN}, "protected": False}
        if path.endswith("/pulls/175"):
            return {"head": {"sha": HEAD}, "base": {"ref": "main"},
                    "state": "open", "draft": True, "mergeable": True}
        if "/actions/runs?" in path:
            return {"workflow_runs": []}
        if "/rulesets?" in path:
            return []
        raise AssertionError(path)

    monkeypatch.setattr(subject, "_gh_get", fake_get)
    subject.live_snapshot(175)
    assert len(calls) == 4
    assert all(not x.startswith(("PUT ", "POST ", "DELETE ")) for x in calls)
    assert any(f"head_sha={HEAD}" in x for x in calls)


def test_live_permission_error_is_never_a_success(monkeypatch):
    def forbidden(_):
        raise subprocess.CalledProcessError(1, ["gh", "api"])

    monkeypatch.setattr(subject, "_gh_get", forbidden)
    with pytest.raises(subprocess.CalledProcessError):
        subject.live_snapshot(175)
