"""Regression checks for V7 integration audit; synthetic fixtures only."""
from scripts.v7_pr_head_audit import assess, run

H = "a" * 40
M = "b" * 40


def fixture():
    pr = {"number": 42, "state": "open", "draft": False, "mergeable": True,
          "mergeable_state": "clean", "base": {"ref": "main", "sha": M},
          "head": {"sha": H}}
    main = {"commit": {"sha": M}}
    checks = [{"name": "tests-and-full-match", "head_sha": H,
               "status": "completed", "conclusion": "success",
               "app": {"slug": "github-actions"}}]
    return pr, main, checks


def test_clean_pr_remains_manual_review_only():
    data = assess(*fixture(), H, M)
    assert data["preliminary_status"] == "needs_integrator_review"
    assert data["merge_authorized"] is False
    assert "exclusive_integration_lease" in data["not_checked"]


def test_draft_and_wrong_main_fail_closed():
    p, b, c = fixture()
    p["draft"] = True
    b["commit"]["sha"] = "c" * 40
    d = assess(p, b, c, H, M)
    assert "pr_draft_or_unknown" in d["blockers"]
    assert "main_sha_changed" in d["blockers"]


def test_stale_head_or_stale_base_blocks():
    p, b, c = fixture()
    p["head"]["sha"] = "c" * 40
    p["base"]["sha"] = "d" * 40
    d = assess(p, b, c, H, M)
    assert "head_sha_changed" in d["blockers"]
    assert "pr_base_not_current_main" in d["blockers"]


def test_queued_or_old_head_ci_not_success():
    p, b, c = fixture()
    c[0]["status"] = "queued"
    assert "no_successful_exact_head_full_match_check" in assess(p, b, c, H, M)["blockers"]
    c[0]["status"] = "completed"
    c[0]["head_sha"] = "c" * 40
    assert "no_successful_exact_head_full_match_check" in assess(p, b, c, H, M)["blockers"]


def test_foreign_app_check_cannot_substitute_for_github_actions():
    p, b, c = fixture()
    c[0]["app"]["slug"] = "external-ci"
    assert assess(p, b, c, H, M)["preliminary_status"] == "blocked"


def test_unknown_mergeable_is_not_accepted():
    p, b, c = fixture()
    p["mergeable"] = None
    assert "mergeability_not_verified" in assess(p, b, c, H, M)["blockers"]


def test_invalid_input_fails_before_network():
    import pytest
    with pytest.raises(ValueError):
        run("sstxww/reinforcement-learning", 8, "short", M)
    with pytest.raises(ValueError):
        run("bad-path/../repo", 8, H, M)
