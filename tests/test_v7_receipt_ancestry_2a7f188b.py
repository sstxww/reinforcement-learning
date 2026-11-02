"""Synthetic receipts and temporary git repos; never actual game evidence."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.v7_receipt_ancestry_2a7f188b import verify_ancestry
from tavern_ai.contract import ENGINE_HASH


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


@pytest.fixture
def history(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    path = repo / "foo.txt"
    path.write_text("first")
    git(repo, "add", "foo.txt")
    git(repo, "commit", "-qm", "first")
    first = git(repo, "rev-parse", "HEAD")
    path.write_text("second")
    git(repo, "commit", "-qam", "second")
    second = git(repo, "rev-parse", "HEAD")
    return repo, first, second


def synthetic_receipt(sha):
    return {
        "environment": "TavernGym", "completed": True,
        "agent_id": "synthetic-test-only",
        "placements": [1, 2, 3, 4, 5, 6, 7, 8],
        "turns": 2, "decisions": 4, "truncated_combats": 0,
        "turn_limit_end": False, "seed": 1, "engine_version": "1.1.0",
        "engine_source_hash": ENGINE_HASH,
        "policy": "baseline", "model_sha256": None, "git_sha": sha,
    }


def test_ancestor_is_version_linked_but_not_authenticity_proof(history):
    repo, first, second = history
    result = verify_ancestry(synthetic_receipt(first), head=second, repo=repo)
    assert result["ancestor_verified"] is True
    assert result["authentic_game_proven"] is False


def test_missing_or_placeholder_source_is_rejected(history):
    repo, _, second = history
    for bad in ("", None, "0" * 10):
        with pytest.raises(ValueError, match="game git_sha"):
            verify_ancestry(synthetic_receipt(bad), head=second, repo=repo)


def test_newer_game_cannot_be_claimed_by_older_head(history):
    repo, first, second = history
    with pytest.raises(ValueError, match="not an ancestor"):
        verify_ancestry(synthetic_receipt(second), head=first, repo=repo)


def test_bad_placement_not_accepted(history):
    repo, first, second = history
    receipt = synthetic_receipt(first)
    receipt["placements"] = [1] * 8
    with pytest.raises(ValueError):
        verify_ancestry(receipt, head=second, repo=repo)


def test_shallow_clone_requires_explicit_full_history(history, monkeypatch):
    repo, first, second = history
    original = subprocess.run
    def fake_run(argv, **kwargs):
        if "--is-shallow-repository" in argv:
            return subprocess.CompletedProcess(argv, 0, stdout="true\n", stderr="")
        return original(argv, **kwargs)
    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(ValueError, match="full git history"):
        verify_ancestry(synthetic_receipt(first), head=second, repo=repo)
