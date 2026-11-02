"""Offline fail-closed mutation tests for the V7 read-only integration gate."""
from copy import deepcopy

from scripts.v7_merge_gate_aadbbf93 import assess

MAIN = "a" * 40
HEAD = "b" * 40
SESSION = "s-20261103-aadbbf93"
RECEIPT = f"experiments/{SESSION}/001-99673.json"


def valid():
    pr = {
        "number": 999, "state": "open", "draft": False,
        "mergeable": True, "mergeable_state": "clean",
        "base": {"ref": "main", "sha": MAIN},
        "head": {"sha": HEAD, "ref": f"agent/{SESSION}/optimization-001",
                 "repo": {"full_name": "sstxww/reinforcement-learning"}},
    }
    run = {
        "id": 321, "name": "CI - full-match gate", "event": "pull_request",
        "head_sha": HEAD, "status": "completed", "conclusion": "success",
        "created_at": "2026-11-03T00:00:00Z",
        "html_url": "https://github.com/sstxww/reinforcement-learning/actions/runs/321",
    }
    jobs = {321: {"total_count": 1,
                  "jobs": [{"name": "tests-and-full-match", "status": "completed",
                            "conclusion": "success"}]}}
    receipt = {
        "schema": 1, "timestamp": "2026-11-03T00:00:00+00:00",
        "environment": "TavernGym", "engine_version": "1.1.0",
        "engine_source_hash": "6d8712c93022ba11",
        "agent_id": SESSION, "policy": "baseline",
        "seed": 99673, "completed": True, "turns": 17,
        "decisions": 47, "placements": [7, 4, 2, 8, 1, 6, 3, 5],
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": None,
    }
    return pr, [run], jobs, ["scripts/v7_merge_gate_aadbbf93.py", RECEIPT], receipt


def verdict(pr=None, runs=None, jobs=None, changed=None, receipt=None,
            main=MAIN, expected_main=MAIN, expected_head=HEAD):
    p, r, j, c, x = valid()
    return assess(pr if pr is not None else p, main, expected_main, expected_head,
                  runs if runs is not None else r, jobs if jobs is not None else j,
                  changed if changed is not None else c, RECEIPT,
                  receipt if receipt is not None else x)


def test_good_candidate_is_only_ready_for_review_not_merged():
    result = verdict()
    assert result["ready_for_exclusive_integration_review"] is True
    assert result["merge_performed"] is False
    assert result["review_and_exclusive_integration_lease_required"] is True


def test_moving_main_and_pr_head_fail_closed():
    p, *_ = valid()
    p["head"]["sha"] = "c" * 40
    assert not verdict(pr=p)["ready_for_exclusive_integration_review"]
    assert not verdict(main="c" * 40)["ready_for_exclusive_integration_review"]


def test_draft_or_stacked_pr_or_unclean_cannot_pass():
    for mutation in ("draft", "stacked", "conflict"):
        p, *_ = valid()
        if mutation == "draft":
            p["draft"] = True
        elif mutation == "stacked":
            p["base"]["ref"] = "agent/learning/v1"
        else:
            p["mergeable_state"] = "dirty"
        assert not verdict(pr=p)["ready_for_exclusive_integration_review"]


def test_prior_green_run_cannot_mask_latest_failure():
    _, runs, jobs, _, _ = valid()
    failed = deepcopy(runs[0])
    failed.update(id=322, created_at="2026-11-03T00:01:00Z", conclusion="failure")
    jobs[322] = {"total_count": 1, "jobs": [
        {"name": "tests-and-full-match", "status": "completed", "conclusion": "failure"}]}
    result = verdict(runs=runs + [failed], jobs=jobs)
    assert not result["ready_for_exclusive_integration_review"]
    assert "Latest-head CI did not complete successfully" in result["blockers"]


def test_empty_action_required_or_truncated_jobs_cannot_pass():
    _, runs, jobs, _, _ = valid()
    jobs[321] = {"total_count": 1, "jobs": []}
    assert not verdict(jobs=jobs)["ready_for_exclusive_integration_review"]
    runs[0]["conclusion"] = "action_required"
    assert not verdict(runs=runs)["ready_for_exclusive_integration_review"]


def test_no_real_own_receipt_cannot_pass():
    _, _, _, changed, receipt = valid()
    assert not verdict(changed=changed[:1])["ready_for_exclusive_integration_review"]
    receipt["agent_id"] = "s-20261103-another"
    assert not verdict(receipt=receipt)["ready_for_exclusive_integration_review"]


def test_assisted_and_invalid_receipts_fail_closed():
    for field, value in (("guard_forced_ends", 1), ("fallback_actions", 1),
                         ("raw_model_only", False), ("guarded", True),
                         ("turn_limit_end", True)):
        _, _, _, _, receipt = valid()
        receipt[field] = value
        assert not verdict(receipt=receipt)["ready_for_exclusive_integration_review"]


def test_model_weights_must_not_be_committed():
    _, _, _, changed, _ = valid()
    assert not verdict(changed=changed + ["models/candidate.zip"])["ready_for_exclusive_integration_review"]
