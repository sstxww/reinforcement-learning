"""Synthetic API regression cases. They are NOT TavernGym match evidence."""
import importlib.util
from pathlib import Path

import pytest

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "v7_main_ci_attestation_fea0d63f.py"
)
spec = importlib.util.spec_from_file_location("v7_main_ci_attestation_fea0d63f", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SHA = "a" * 40
OLD_SHA = "b" * 40


def api_fixture(*, main_sha=SHA, runs=None, step_status=None, jobs=None,
                drift_sha=None, missing_steps=()):
    path = ".github/workflows/ci.yml"
    current_run = {
        "id": 99, "run_attempt": 1, "name": "CI - full-match gate",
        "path": path, "head_branch": "main", "head_sha": main_sha,
        "event": "push", "status": "completed", "conclusion": "success",
        "html_url": "https://github.com/sstxww/reinforcement-learning/actions/runs/99",
    }
    if runs is None:
        runs = [current_run]
    if jobs is None:
        jobs = [{
            "name": "tests-and-full-match", "conclusion": "success",
            "html_url": "https://github.com/sstxww/reinforcement-learning/actions/jobs/101",
            "steps": [{"name": s, "conclusion": (step_status or {}).get(s, "success")}
                      for s in mod.REQUIRED_STEPS if s not in missing_steps],
        }]
    state = {"branch_reads": 0, "calls": []}

    def get(url):
        state["calls"].append(url)
        if url.endswith("/branches/main"):
            state["branch_reads"] += 1
            reported = drift_sha if state["branch_reads"] > 1 and drift_sha else main_sha
            return {"commit": {"sha": reported}}
        if url.endswith("/actions/runs?branch=main&per_page=100"):
            return {"workflow_runs": runs}
        if url.endswith("/actions/runs/99/jobs?per_page=100"):
            return {"total_count": len(jobs), "jobs": jobs}
        raise AssertionError("Unexpected fake GitHub URL: " + url)

    return get, state


def test_exact_main_job_and_all_required_steps_accepted():
    get, state = api_fixture()
    result = mod.attest(get)
    assert result["main_sha"] == SHA
    assert result["run_id"] == 99
    assert result["status"] == "exact_main_ci_steps_verified"
    assert result["merge_lock_held"] is False
    assert result["model_improvement_claimed"] is False
    assert result["post_merge_artifact_bytes_verified"] is False
    assert state["branch_reads"] == 2


def test_successful_old_commit_run_not_sufficient():
    stale = {
        "id": 99, "run_attempt": 1, "name": "CI - full-match gate",
        "path": ".github/workflows/ci.yml", "head_branch": "main",
        "head_sha": OLD_SHA, "event": "push",
        "status": "completed", "conclusion": "success",
    }
    get, _ = api_fixture(runs=[stale])
    with pytest.raises(ValueError, match="exact current main"):
        mod.attest(get)


def test_newer_failed_exact_sha_cannot_be_hidden_by_older_success():
    success = {
        "id": 98, "run_attempt": 1, "name": "CI - full-match gate",
        "path": ".github/workflows/ci.yml", "head_branch": "main",
        "head_sha": SHA, "event": "push",
        "status": "completed", "conclusion": "success",
    }
    failed = dict(success, id=100, conclusion="failure")
    get, _ = api_fixture(runs=[success, failed])
    with pytest.raises(ValueError, match="pending, cancelled, or unsuccessful"):
        mod.attest(get)


@pytest.mark.parametrize("conclusion", ["failure", "skipped", "cancelled", None])
def test_latest_run_not_success_is_rejected(conclusion):
    get, _ = api_fixture()
    original = {
        "id": 99, "run_attempt": 1, "name": "CI - full-match gate",
        "path": ".github/workflows/ci.yml", "head_branch": "main",
        "head_sha": SHA, "event": "push",
        "status": "completed", "conclusion": conclusion,
    }
    get, _ = api_fixture(runs=[original])
    with pytest.raises(ValueError, match="unsuccessful"):
        mod.attest(get)


@pytest.mark.parametrize("step", mod.REQUIRED_STEPS)
def test_all_mandatory_steps_proved(step):
    get, _ = api_fixture(missing_steps=(step,))
    with pytest.raises(ValueError, match="Required successful CI step missing"):
        mod.attest(get)
    get, _ = api_fixture(step_status={step: "failure"})
    with pytest.raises(ValueError, match="Required successful CI step missing"):
        mod.attest(get)


def test_main_moves_during_attestation_fails_closed():
    get, state = api_fixture(drift_sha=OLD_SHA)
    with pytest.raises(ValueError, match="Main changed"):
        mod.attest(get)
    assert state["branch_reads"] == 2


def test_expected_main_sha_mismatch_fails_early():
    get, state = api_fixture()
    with pytest.raises(ValueError, match="Main moved"):
        mod.attest(get, expected_main_sha=OLD_SHA)
    assert state["branch_reads"] == 1


def test_wrong_workflow_and_pr_event_are_excluded():
    current = {
        "id": 99, "run_attempt": 1, "name": "CI - full-match gate",
        "path": ".github/workflows/ci.yml", "head_branch": "main",
        "head_sha": SHA, "event": "pull_request",
        "status": "completed", "conclusion": "success",
    }
    get, _ = api_fixture(runs=[current])
    with pytest.raises(ValueError, match="exact current main"):
        mod.attest(get)


def test_missing_successful_job_is_rejected():
    get, _ = api_fixture(jobs=[])
    with pytest.raises(ValueError, match="Required full-match job"):
        mod.attest(get)


def test_wrong_repo_rejected_without_api_calls():
    get, state = api_fixture()
    with pytest.raises(ValueError, match="authorized repository"):
        mod.attest(get, repository="other/repository")
    assert state["calls"] == []
