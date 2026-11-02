"""Default-capacity regression: read-only integration audit must include all 116 PRs."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re

import pytest

spec = importlib.util.spec_from_file_location(
    "v5_pr_gate_capacity",
    Path(__file__).resolve().parents[1] / "scripts" / "v5_pr_gate_bb9904e5.py",
)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def _fake_api(path: str):
    root = "/repos/sstxww/reinforcement-learning"
    if path == root + "/branches/main":
        return {"commit": {"sha": "a" * 40}}
    if path.startswith(root + "/pulls?state=open&per_page=100&page="):
        page = int(path.rsplit("=", 1)[1])
        numbers = range(1, 117)
        start = (page - 1) * 100
        return [{"number": n} for n in list(numbers)[start:start + 100]]
    match = re.fullmatch(re.escape(root) + r"/pulls/(\d+)", path)
    if match:
        n = int(match.group(1))
        return {
            "number": n, "title": f"Isolated audit {n}", "body": "read only",
            "html_url": f"https://github.com/sstxww/reinforcement-learning/pull/{n}",
            "draft": True, "mergeable_state": "clean",
            "head": {"sha": f"{n:040x}"}, "base": {"ref": "main"},
        }
    if path.startswith(root + "/actions/runs?head_sha="):
        return {"workflow_runs": []}
    raise AssertionError(f"Unexpected API call: {path}")


def test_current_116_prs_are_audited_by_default_without_truncation(monkeypatch):
    monkeypatch.setattr(gate, "api_get", _fake_api)
    result = gate.audit("sstxww/reinforcement-learning")
    assert result["open_pr_count"] == result["scanned_pr_count"] == 116
    assert {row["number"] for row in result["pull_requests"]} == set(range(1, 117))
    assert result["main_stable_during_scan"] is True
    assert result["automated_merge_approved"] is False
    assert all(row["category"].startswith("B_") for row in result["pull_requests"])


def test_custom_too_small_cap_still_fails_closed(monkeypatch):
    monkeypatch.setattr(gate, "api_get", _fake_api)
    with pytest.raises(RuntimeError, match=r"exceeds max_prs=100"):
        gate.audit("sstxww/reinforcement-learning", max_prs=100)
