"""Focused non-network regression tests for the V5 PR inventory."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "v5_pr_gate", Path(__file__).resolve().parents[1] / "scripts" / "v5_pr_gate_bb9904e5.py"
)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def sample(**overrides):
    pr = {
        "title": "Add read-only evaluation audit",
        "body": "tests, receipts and no claim of neural gain",
        "draft": False,
        "base": {"ref": "main"},
        "mergeable_state": "clean",
    }
    pr.update(overrides)
    return pr


def ci(state="success"):
    return {"state": state, "url": None, "run_id": None}


def test_only_exact_head_full_game_pr_ci_is_accepted():
    good = {
        "head_sha": "a" * 40, "name": "CI - full-match gate", "event": "pull_request",
        "created_at": "2026-11-02T00:00:00Z", "id": 10,
        "status": "completed", "conclusion": "success",
    }
    assert gate.latest_head_ci([{**good, "head_sha": "b" * 40}], "a" * 40)["state"] == "missing"
    assert gate.latest_head_ci([{**good, "event": "push"}], "a" * 40)["state"] == "missing"
    assert gate.latest_head_ci([{**good, "name": "Some other CI"}], "a" * 40)["state"] == "missing"
    assert gate.latest_head_ci([good], "a" * 40)["state"] == "success"
    newer = {**good, "id": 11, "created_at": "2026-11-02T01:00:00Z", "status": "queued", "conclusion": None}
    assert gate.latest_head_ci([good, newer], "a" * 40)["state"] == "pending"


def test_conflicted_pr_is_never_merge_candidate():
    bucket, blockers = gate.classify(sample(mergeable_state="dirty"), ci())
    assert bucket == "E_conflict_or_overlap"
    assert any("conflict" in b.lower() for b in blockers)


def test_draft_and_stacked_prs_never_merge_ready():
    assert gate.classify(sample(draft=True), ci())[0].startswith("B_")
    assert gate.classify(sample(base={"ref": "agent/learning/v1"}), ci())[0].startswith("B_")


@pytest.mark.parametrize("state", ["missing", "pending", "failure", "cancelled", "action_required"])
def test_no_head_success_is_blocked(state):
    assert gate.classify(sample(), ci(state))[0].startswith("B_")


def test_negative_experiment_cannot_promote_despite_green_ci():
    bucket, blockers = gate.classify(sample(title="Twenty real games, no strength gain"), ci())
    assert bucket == "D_negative_or_no_gain"
    assert "promotion" in " ".join(blockers)


def test_performance_pr_requires_heldout_review():
    bucket, blockers = gate.classify(sample(title="PPO new policy improvement"), ci())
    assert bucket == "C_performance_review_required"
    assert "held-out" in " ".join(blockers)


def test_green_engineering_pr_is_only_a_manual_review_candidate():
    bucket, blockers = gate.classify(sample(), ci())
    assert bucket == "A_engineering_review_candidate"
    assert "Manual" in " ".join(blockers)


@pytest.mark.parametrize("repo", [
    "../../etc", "user/repo/contents", "https://github.com/user/repo", "user\\n/repo", "",
])
def test_invalid_repository_rejected(repo):
    with pytest.raises(ValueError):
        gate.repo_path(repo)
