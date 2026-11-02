"""Negative and positive tests: no live GitHub merge side effects."""
import pytest
from scripts.v7_serial_integrator import (
    GateError, check_pr, check_reviews, check_run, check_jobs, check_sensitive_paths, sha
)

HEAD = "a" * 40
BASE = "b" * 40
REPO = "sstxww/reinforcement-learning"

def pr():
    return {"number": 42, "state": "open", "draft": False,
            "base": {"ref": "main", "sha": BASE},
            "head": {"sha": HEAD, "repo": {"full_name": REPO}},
            "mergeable": True, "mergeable_state": "clean"}

def test_exact_pr_identity_and_mergeable():
    check_pr(pr(), REPO, 42, HEAD, BASE)
    for field, bad in (("draft", True), ("mergeable", None), ("mergeable_state", "dirty")):
        p = pr()
        p[field] = bad
        with pytest.raises(GateError):
            check_pr(p, REPO, 42, HEAD, BASE)
    p = pr()
    p["base"]["sha"] = HEAD
    with pytest.raises(GateError):
        check_pr(p, REPO, 42, HEAD, BASE)
    p = pr()
    p["head"]["repo"]["full_name"] = "other/fork"
    with pytest.raises(GateError):
        check_pr(p, REPO, 42, HEAD, BASE)

def test_reviews_require_non_author_exact_head_approval():
    good = [{"user": {"login": "reviewer"}, "state": "APPROVED",
             "commit_id": HEAD, "submitted_at": "2026-11-02T19:00:00Z"}]
    check_reviews(good, "author", HEAD)
    with pytest.raises(GateError):
        check_reviews(good, "reviewer", HEAD)
    with pytest.raises(GateError):
        check_reviews([dict(good[0], commit_id=BASE)], "author", HEAD)
    with pytest.raises(GateError):
        check_reviews(good + [{"user": {"login": "other"}, "state": "CHANGES_REQUESTED",
                               "submitted_at": "2026-11-02T19:02:00Z"}], "author", HEAD)

def test_latest_ci_exact_head_after_main_and_not_pending():
    good = {"id": 7, "event": "pull_request", "head_sha": HEAD,
            "name": "CI - full-match gate", "path": ".github/workflows/ci.yml",
            "pull_requests": [{"number": 42}], "created_at": "2026-11-02T19:10:00Z",
            "run_started_at": "2026-11-02T19:10:00Z",
            "status": "completed", "conclusion": "success"}
    assert check_run([good], 42, HEAD, "2026-11-02T19:00:00Z")["id"] == 7
    with pytest.raises(GateError):
        check_run([good], 42, HEAD, "2026-11-02T19:20:00Z")
    with pytest.raises(GateError):
        check_run([good, dict(good, id=8, status="in_progress", conclusion=None,
                              created_at="2026-11-02T19:11:00Z")], 42, HEAD, "2026-11-02T19:00:00Z")
    with pytest.raises(GateError):
        check_run([dict(good, pull_requests=[{"number": 43}])], 42, HEAD,
                  "2026-11-02T19:00:00Z")

def test_require_full_eight_seat_job_and_preserved_receipt():
    names = ("Unit tests and PR evidence", "Install pinned engine and verified patch",
             "Confirm engine layout", "Real full eight-seat simulated match",
             "Preserve CI evidence")
    good = {"name": "tests-and-full-match", "conclusion": "success",
            "steps": [{"name": n, "conclusion": "success"} for n in names]}
    check_jobs([good])
    with pytest.raises(GateError):
        check_jobs([dict(good, steps=good["steps"][:-1])])
    with pytest.raises(GateError):
        check_jobs([dict(good, conclusion="failure")])

def test_reject_invalid_sha():
    assert sha(HEAD) == HEAD
    for value in ("short", "../" + HEAD, HEAD.upper(), ""):
        with pytest.raises(GateError):
            sha(value)

def test_pr_cannot_redefine_evidence_workflow_or_gate():
    check_sensitive_paths([{"filename": "tavern_ai/model.py"}])
    for critical in (".github/workflows/ci.yml", "scripts/check_pr_evidence.py",
                     "tavern_ai/receipt_integrity.py",
                     ".github/workflows/v7-serialized-integrator.yml"):
        with pytest.raises(GateError):
            check_sensitive_paths([{"filename": critical}])
    with pytest.raises(GateError):
        check_sensitive_paths([{"filename": f"file-{i}"} for i in range(100)])
