"""Regression checks for fail-closed PR pre-review auditing."""
from tavern_ai.integration_triage_c4b19f20 import build_report, inspect_pr

SHA = "a" * 40


def pr(**changes):
    item = {"number": 17, "title": "Safe fixture", "state": "open", "draft": False,
            "head_sha": SHA, "base": "main", "mergeable": True}
    item.update(changes)
    return item


def run(**changes):
    item = {"id": 1, "name": "CI - full-match gate", "head_sha": SHA,
            "event": "pull_request", "status": "completed", "conclusion": "success"}
    item.update(changes)
    return item


def test_even_green_full_match_ci_does_not_authorize_merge():
    result = inspect_pr(pr(), [run()])
    assert result["status"] == "requires_independent_manual_review"
    assert result["merge_authorized"] is False
    assert result["pre_review_blockers"] == []


def test_draft_must_not_be_merged_even_with_green_ci():
    result = inspect_pr(pr(draft=True), [run()])
    assert "draft_or_unknown_draft_state" in result["pre_review_blockers"]


def test_stacked_base_is_blocked_until_dependency_integrated():
    result = inspect_pr(pr(base="agent/learning/v1"), [run()])
    assert "stacked_or_unknown_base_dependency" in result["pre_review_blockers"]


def test_stale_green_ci_does_not_count():
    result = inspect_pr(pr(), [run(head_sha="b" * 40)])
    assert "no_latest_head_full_match_pr_ci" in result["pre_review_blockers"]


def test_action_required_is_not_a_test_pass():
    result = inspect_pr(pr(), [run(status="completed", conclusion="action_required")])
    assert "latest_head_full_match_ci_unverified" in result["pre_review_blockers"]


def test_mergeability_unknown_or_conflict_fails_closed():
    assert "conflict_or_unresolved_mergeability" in inspect_pr(pr(mergeable=None), [run()])["pre_review_blockers"]
    assert "conflict_or_unresolved_mergeability" in inspect_pr(pr(mergeable=False), [run()])["pre_review_blockers"]


def test_pr_list_missing_number_or_head_is_blocked():
    result = inspect_pr(pr(number=None, head_sha=None), [])
    assert "missing_pr_number" in result["pre_review_blockers"]
    assert "missing_exact_head_sha" in result["pre_review_blockers"]


def test_rest_pr_nested_refs_are_supported():
    data = pr()
    data.pop("head_sha")
    data["head"] = {"sha": SHA}
    data["base"] = {"ref": "main"}
    assert inspect_pr(data, [run()])["pre_review_blockers"] == []


def test_read_only_report_totals_and_precludes_automatic_merges():
    report = build_report([pr(), pr(number=18, draft=True)], [run()])
    assert report["sample_size"] == 2
    assert report["blocked"] == 1
    assert report["needs_manual_review"] == 1
    assert all(not p["merge_authorized"] for p in report["pull_requests"])
