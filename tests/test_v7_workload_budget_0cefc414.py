"""Fail-closed regression tests for the read-only advisory V7 workflow budget."""
import pytest
from scripts.v7_workload_budget_0cefc414 import ACTIVE, BudgetError, preflight, summarize

def pages(items=()):
    p = {status: {"total_count": 0, "workflow_runs": []} for status in ACTIVE}
    for ident, status, name in items:
        p[status]["workflow_runs"].append({"id": ident, "status": status, "name": name})
        p[status]["total_count"] += 1
    return p

def test_valid_snapshot_counts_heavy_and_total_without_false_merge_lease():
    result = summarize(pages([(1, "queued", "V7 - PPO continuation"),
                              (2, "in_progress", "CI - full-match gate"),
                              (3, "waiting", "self-play smoke")]))
    assert (result["active_total"], result["named_training_total"]) == (3, 2)
    assert result["scope"] == "advisory_snapshot_not_atomic"
    assert result["training_run_ids"] == [1, 3]
    assert preflight(result, max_active=4, max_training=3) is result
    with pytest.raises(BudgetError, match="threshold"):
        preflight(result, max_active=3, max_training=3)
    with pytest.raises(BudgetError, match="threshold"):
        preflight(result, max_active=4, max_training=2)

def test_exclude_only_own_known_run_and_fail_closed_on_bad_id():
    p = pages([(11, "in_progress", "PPO train"), (12, "queued", "CI")])
    assert summarize(p, own_run_id=11)["active_total"] == 1
    p["queued"]["workflow_runs"][0]["id"] = "12"
    with pytest.raises(BudgetError, match="identity"):
        summarize(p)

def test_reject_incomplete_pagination_and_absent_status():
    p = pages([(1, "queued", "CI")])
    p["queued"]["total_count"] += 101
    with pytest.raises(BudgetError, match="pagination"):
        summarize(p)
    p = pages()
    del p["waiting"]
    with pytest.raises(BudgetError, match="coverage"):
        summarize(p)

def test_reject_mismatched_status_and_duplicate_run():
    p = pages([(7, "queued", "train")])
    p["queued"]["workflow_runs"][0]["status"] = "completed"
    with pytest.raises(BudgetError, match="mismatch"):
        summarize(p)
    p = pages([(7, "queued", "train"), (7, "in_progress", "train")])
    with pytest.raises(BudgetError, match="Conflicting"):
        summarize(p)

def test_reject_invalid_thresholds_and_missing_runs():
    p = pages()
    assert preflight(summarize(p), 1, 1)["active_total"] == 0
    with pytest.raises(BudgetError, match="positive"):
        preflight(summarize(p), 0, 1)
    p["in_progress"] = {"total_count": 1}
    with pytest.raises(BudgetError, match="workflow_runs"):
        summarize(p)
