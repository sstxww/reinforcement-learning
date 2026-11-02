"""Synthetic offline gate regressions; these are NOT TavernGym match receipts."""
import pytest
from scripts.v7_main_ci_gate_f6c9fea8 import REQUIRED_STEPS, verify

SHA = "a" * 40
OTHER = "b" * 40


def branch(sha=SHA):
    return {"commit": {"sha": sha}}


def run(sha=SHA, ident=100, status="completed", conclusion="success", event="push"):
    return {"head_sha": sha, "name": "CI - full-match gate",
            "head_branch": "main", "event": event, "id": ident,
            "run_attempt": 1, "status": status, "conclusion": conclusion,
            "html_url": "https://github.com/example/actions/runs/100"}


def jobs():
    return [{"name": "tests-and-full-match", "conclusion": "success",
             "steps": [{"name": n, "conclusion": "success"} for n in REQUIRED_STEPS]}]


def test_valid_gate_precheck_is_not_a_merge_lease():
    outcome = verify(branch(), [run()], jobs(), branch())
    assert outcome["ready_for_integration_review"] is True
    assert outcome["main_sha"] == SHA
    assert "not merge lease" in outcome["scope"]


def test_old_green_sha_rejected():
    with pytest.raises(ValueError, match="No exact-main-head"):
        verify(branch(), [run(OTHER)], jobs(), branch())


def test_main_move_during_check_rejected():
    with pytest.raises(ValueError, match="main moved"):
        verify(branch(), [run()], jobs(), branch(OTHER))


@pytest.mark.parametrize("status,conclusion", [
    ("in_progress", None), ("completed", "failure"), ("completed", "cancelled")
])
def test_latest_pending_or_bad_ci_is_not_green(status, conclusion):
    with pytest.raises(ValueError, match="pending, failed"):
        verify(branch(), [run(status=status, conclusion=conclusion)], jobs(), branch())


def test_newer_failed_run_supersedes_older_success():
    with pytest.raises(ValueError, match="pending, failed"):
        verify(branch(), [run(ident=98),
               run(ident=101, conclusion="failure")], jobs(), branch())


@pytest.mark.parametrize("missing", REQUIRED_STEPS)
def test_missing_step_rejected(missing):
    altered = jobs()
    altered[0]["steps"] = [x for x in altered[0]["steps"] if x["name"] != missing]
    with pytest.raises(ValueError, match="Missing or failed"):
        verify(branch(), [run()], altered, branch())


def test_failed_step_or_job_rejected():
    altered = jobs()
    altered[0]["steps"][0]["conclusion"] = "failure"
    with pytest.raises(ValueError, match="Missing or failed"):
        verify(branch(), [run()], altered, branch())
    altered = jobs()
    altered[0]["conclusion"] = "failure"
    with pytest.raises(ValueError, match="Missing or unsuccessful"):
        verify(branch(), [run()], altered, branch())


def test_pr_triggered_ci_not_a_main_push():
    with pytest.raises(ValueError, match="No exact-main-head"):
        verify(branch(), [run(event="pull_request")], jobs(), branch())


def test_malformed_sha_rejected():
    with pytest.raises(ValueError, match="Missing trustworthy"):
        verify(branch("invalid"), [run()], jobs(), branch())


def test_missing_step_array_rejected():
    altered = jobs()
    altered[0].pop("steps")
    with pytest.raises(ValueError, match="Missing CI job step"):
        verify(branch(), [run()], altered, branch())
