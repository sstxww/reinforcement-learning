"""Regression: PR must not satisfy a CI-by-step-name gate after editing its commands."""
import importlib.util
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts/v7_ci_definition_guard_223b16589f.py"
spec = importlib.util.spec_from_file_location("v7_ci_definition_guard", PATH)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

HEAD, MAIN = "a" * 40, "b" * 40
REPO = "sstxww/reinforcement-learning"


def row(path, **kwargs):
    item = {"filename": path, "status": "modified"}
    item.update(kwargs)
    return item


@pytest.mark.parametrize("critical", sorted(guard.CRITICAL))
def test_reject_each_trusted_ci_definition_change(critical):
    with pytest.raises(guard.GateError, match="trust-boundary"):
        guard.check_changed_files([row(critical)])


def test_reject_renaming_critical_file_out_of_way():
    with pytest.raises(guard.GateError, match="trust-boundary"):
        guard.check_changed_files([row("temporary/old-ci.yml", status="renamed",
                                       previous_filename=".github/workflows/ci.yml")])


def test_allow_isolated_session_code_and_game_receipts():
    outcome = guard.check_changed_files([
        row("scripts/s-unique-audit.py"),
        row("tests/test_s_unique.py"),
        row("experiments/s-unique/001-99681.json"),
        row("research/sessions/s-unique/STATUS.md"),
    ])
    assert outcome["checked_files"] == 4
    assert outcome["decision"] == "pass"


@pytest.mark.parametrize("bad", ["/x", "../x", "a/../b", "a//b", "a/./b",
                                    "foo\\bar", "", None])
def test_reject_noncanonical_changed_file_paths(bad):
    with pytest.raises(guard.GateError):
        guard.check_changed_files([row(bad)])


def test_reject_missing_duplicate_and_unbounded_evidence():
    for files in ([], [row("x"), row("x")], [row("x")] * 3001, [{}]):
        with pytest.raises(guard.GateError):
            guard.check_changed_files(files)


class FakeGitHub:
    repository = REPO

    def __init__(self, files, *, drift=False, changed_head=False):
        self.files = files
        self.drift = drift
        self.changed_head = changed_head
        self.main_calls = 0
        self.pr_calls = 0

    def get(self, suffix):
        if suffix == "/branches/main":
            self.main_calls += 1
            return {"commit": {"sha": "c" * 40 if self.drift and self.main_calls > 1 else MAIN}}
        if suffix == "/pulls/42":
            self.pr_calls += 1
            return {"number": 42, "state": "open", "draft": False,
                    "base": {"ref": "main", "sha": MAIN},
                    "head": {"sha": "d" * 40 if self.changed_head and self.pr_calls > 1 else HEAD,
                             "repo": {"full_name": REPO}}}
        if suffix.startswith("/pulls/42/files?"):
            page = int(suffix.split("page=")[-1])
            return self.files[(page - 1) * 100:page * 100]
        raise AssertionError("Unexpected API read: " + suffix)


def test_live_read_contract_paginates_and_double_checks_identity():
    api = FakeGitHub([row(f"research/a-{i}.txt") for i in range(102)])
    result = guard.inspect(api, 42, HEAD, MAIN)
    assert result["checked_files"] == 102
    assert api.pr_calls == 2 and api.main_calls == 2


def test_live_read_rejects_concurrent_main_or_head_change():
    for opts in ({"drift": True}, {"changed_head": True}):
        with pytest.raises(guard.GateError):
            guard.inspect(FakeGitHub([row("research/a.md")], **opts), 42, HEAD, MAIN)


def test_live_read_rejects_trusted_ci_change_on_second_page():
    files = [row(f"research/item-{i}.txt") for i in range(100)]
    files.append(row(".github/workflows/ci.yml"))
    with pytest.raises(guard.GateError, match="trust-boundary"):
        guard.inspect(FakeGitHub(files), 42, HEAD, MAIN)
