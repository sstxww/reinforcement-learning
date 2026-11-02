"""Synthetic integration preflight regressions; NOT real game or merge evidence."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

MOD_PATH = Path(__file__).resolve().parents[1] / "scripts" / "v7_pr_gate_0a059dfe.py"
SPEC = spec_from_file_location("v7_pr_gate_s_20261103_0a059dfe", MOD_PATH)
subject = module_from_spec(SPEC)
SPEC.loader.exec_module(subject)

HEAD = "a" * 40
MAIN = "b" * 40


def fixtures():
    pr = {"number": 42, "state": "open", "draft": False, "mergeable_state": "clean",
          "head": {"sha": HEAD}, "base": {"ref": "main", "sha": MAIN}}
    runs = [{"id": 112, "name": "CI - full-match gate", "status": "completed",
             "conclusion": "success", "event": "pull_request", "head_sha": HEAD,
             "created_at": "2026-11-03T00:00:00Z", "html_url": "https://github.com/test/runs/112",
             "pull_requests": [{"number": 42, "head": {"sha": HEAD}, "base": {"sha": MAIN}}]}]
    jobs = {"total_count": 1, "jobs": [{"name": "tests-and-full-match", "conclusion": "success",
             "steps": [{"name": s, "conclusion": "success", "status": "completed"}
                       for s in subject._REQUIRED_STEPS]}]}
    return pr, runs, jobs


def assess(pr, runs, jobs):
    return subject.validate("sstxww/reinforcement-learning", pr, MAIN, HEAD, runs, jobs)


def test_validated_job_is_only_preflight_not_merge_approval():
    got = assess(*fixtures())
    assert got["ci_preflight_passed"] is True
    assert got["merge_authorized"] is False
    assert got["run_id"] == 112


def test_zero_job_success_fails_closed():
    pr, runs, jobs = fixtures()
    jobs = {"total_count": 0, "jobs": []}
    assert "jobs missing" in " ".join(assess(pr, runs, jobs)["blockers"])


def test_pr_head_drift_is_detected():
    pr, runs, jobs = fixtures()
    pr["head"]["sha"] = "c" * 40
    assert not assess(pr, runs, jobs)["ci_preflight_passed"]


def test_ci_attempt_latest_failure_supersedes_old_success():
    pr, runs, jobs = fixtures()
    runs.append({**runs[0], "id": 113, "conclusion": "failure",
                 "created_at": "2026-11-03T00:01:00Z"})
    assert not assess(pr, runs, jobs)["ci_preflight_passed"]


def test_missing_full_match_step_blocks():
    pr, runs, jobs = fixtures()
    jobs["jobs"][0]["steps"] = [s for s in jobs["jobs"][0]["steps"]
                                 if s["name"] != "Real full eight-seat simulated match"]
    assert not assess(pr, runs, jobs)["ci_preflight_passed"]


def test_incomplete_job_pagination_blocks():
    pr, runs, jobs = fixtures()
    jobs["total_count"] = 2
    assert not assess(pr, runs, jobs)["ci_preflight_passed"]


def test_stale_main_or_draft_blocks():
    pr, runs, jobs = fixtures()
    pr["base"]["sha"] = "c" * 40
    assert not assess(pr, runs, jobs)["ci_preflight_passed"]
    pr["base"]["sha"] = MAIN
    pr["draft"] = True
    assert not assess(pr, runs, jobs)["ci_preflight_passed"]


def test_wrong_event_or_skipped_match_not_accepted():
    pr, runs, jobs = fixtures()
    runs[0]["event"] = "push"
    assert not assess(pr, runs, jobs)["ci_preflight_passed"]
    runs[0]["event"] = "pull_request"
    for step in jobs["jobs"][0]["steps"]:
        if step["name"] == "Real full eight-seat simulated match":
            step["conclusion"] = "skipped"
    assert not assess(pr, runs, jobs)["ci_preflight_passed"]


def test_invalid_sha_or_repo_input_refused():
    pr, runs, jobs = fixtures()
    with pytest.raises(ValueError):
        subject.validate("sstxww/../other", pr, MAIN, HEAD, runs, jobs)
    with pytest.raises(ValueError):
        subject.validate("sstxww/reinforcement-learning", pr, MAIN, "short", runs, jobs)


def test_wrong_pr_or_old_tested_base_cannot_reuse_green_ci():
    pr, runs, jobs = fixtures()
    runs[0]["pull_requests"][0]["number"] = 99
    assert not assess(pr, runs, jobs)["ci_preflight_passed"]
    runs[0]["pull_requests"][0]["number"] = 42
    runs[0]["pull_requests"][0]["base"]["sha"] = "c" * 40
    assert not assess(pr, runs, jobs)["ci_preflight_passed"]
