"""Synthetic evidence-gate tests; none of these fixtures are real games."""
from copy import deepcopy
from scripts.v7_main_ci_verify import REQUIRED_STEPS, audit

MAIN = "a" * 40
RUN_ID = 42


def fixture():
    main = {"name": "main", "commit": {"sha": MAIN}}
    run = {"id": RUN_ID, "name": "CI - full-match gate",
           "head_sha": MAIN, "head_branch": "main", "event": "push",
           "status": "completed", "conclusion": "success",
           "html_url": "https://github.com/test/repo/actions/runs/42"}
    jobs = {"jobs": [{"name": "tests-and-full-match",
                      "status": "completed", "conclusion": "success",
                      "steps": [{"name": n, "status": "completed", "conclusion": "success"}
                                for n in REQUIRED_STEPS]}]}
    artifacts = {"artifacts": [{"name": "ci-full-match-42",
                               "expired": False, "size_in_bytes": 313}]}
    return main, run, jobs, artifacts


def test_good_current_main_receipt_step_only_does_not_prove_model_strength():
    result = audit(*fixture())
    assert result["decision"] == "main_ci_verified"
    assert result["integration_lock_verified"] is False
    assert result["model_improvement_verified"] is False


def test_refuses_stale_run_after_main_changes():
    m, r, j, a = fixture()
    m["commit"]["sha"] = "b" * 40
    assert "run head_sha does not match live main" in audit(m, r, j, a)["blockers"]


def test_refuses_manual_and_pr_runs_even_if_green():
    for event in ("workflow_dispatch", "pull_request", "pull_request_target"):
        m, r, j, a = fixture()
        r["event"] = event
        assert audit(m, r, j, a)["decision"] == "blocked"


def test_refuses_pending_or_failed_runs():
    for status, conclusion in (("in_progress", None), ("completed", "failure")):
        m, r, j, a = fixture()
        r["status"], r["conclusion"] = status, conclusion
        assert audit(m, r, j, a)["decision"] == "blocked"


def test_refuses_missing_failed_or_skipped_game_step():
    for step_result in ("skipped", "failure", None):
        m, r, j, a = fixture()
        game = next(x for x in j["jobs"][0]["steps"] if x["name"] == "Real full eight-seat simulated match")
        game["conclusion"] = step_result
        assert "required step not successful: Real full eight-seat simulated match" in audit(m, r, j, a)["blockers"]


def test_refuses_empty_or_expired_receipt_artifact():
    for bad in ({"expired": True}, {"size_in_bytes": 0}, {"name": "wrong"}):
        m, r, j, a = fixture()
        a["artifacts"][0].update(bad)
        assert audit(m, r, j, a)["decision"] == "blocked"


def test_refuses_missing_jobs_and_artifact_list():
    m, r, _, _ = fixture()
    assert audit(m, r, {}, {})["decision"] == "blocked"


def test_refuses_wrong_workflow_or_branch():
    m, r, j, a = fixture()
    m["name"] = "dev"
    r["name"] = "Train"
    assert audit(m, r, j, a)["decision"] == "blocked"


def test_refuses_duplicate_matching_jobs_and_steps():
    m, r, j, a = fixture()
    j["jobs"].append(deepcopy(j["jobs"][0]))
    assert audit(m, r, j, a)["decision"] == "blocked"
    m, r, j, a = fixture()
    j["jobs"][0]["steps"].append(deepcopy(j["jobs"][0]["steps"][0]))
    assert audit(m, r, j, a)["decision"] == "blocked"
