"""Synthetic negative tests. These are NOT real eight-seat match receipts."""
import pytest

from scripts.v7_ci_trust_boundary_8a811e93e9ff import (
    TrustBoundaryError,
    audit_changed_files,
    audit_pr,
    exact_sha,
)

HEAD = "a" * 40
MAIN = "b" * 40


def file(name, status="modified", **kwargs):
    return {"filename": name, "status": status, **kwargs}


def test_benign_isolated_change_passes():
    assert audit_changed_files(
        [file("scripts/new_readonly_diagnostic.py", "added")], 1
    ) == {"checked_files": 1, "trusted_files_modified": 0}


@pytest.mark.parametrize("path", [
    ".github/workflows/ci.yml",
    "tavern_ai/canary.py",
    "tavern_ai/validate_receipt.py",
    "tavern_ai/receipt_integrity.py",
    "scripts/bootstrap_engine.sh",
    "scripts/check_pr_evidence.py",
    "tavern_ai/contract.py",
    "tavern_ai/baseline.py",
    "pyproject.toml",
])
def test_rejects_mutation_of_trusted_full_match_execution(path):
    with pytest.raises(TrustBoundaryError, match="trusted full-match"):
        audit_changed_files([file(path)], 1)


def test_cannot_rename_away_trusted_validator():
    with pytest.raises(TrustBoundaryError, match="trusted full-match"):
        audit_changed_files([
            file("scripts/renamed_evidence.py", "renamed",
                 previous_filename="scripts/check_pr_evidence.py")
        ], 1)


def test_cannot_rename_over_trusted_workflow():
    with pytest.raises(TrustBoundaryError, match="trusted full-match"):
        audit_changed_files([
            file(".github/workflows/ci.yml", "renamed",
                 previous_filename=".github/workflows/ci-disabled.yml")
        ], 1)


@pytest.mark.parametrize("entries,n", [
    ([], 1),
    ([file("x.py")], 2),
    ([file("x.py")], 0),
    ([file("x.py")], 3001),
    ([file("../tavern_ai/canary.py")], 1),
    ([file("scripts\\check_pr_evidence.py")], 1),
    ([file("x.py", "renamed")], 1),
    ([file("x.py", "unknown")], 1),
])
def test_fail_closed_on_malformed_or_incomplete_files(entries, n):
    with pytest.raises(TrustBoundaryError):
        audit_changed_files(entries, n)


def test_fail_closed_on_bad_sha():
    assert exact_sha(HEAD) == HEAD
    for val in ("abc", HEAD.upper(), "", "../" + HEAD, None):
        with pytest.raises(TrustBoundaryError):
            exact_sha(val)


class FakeReadOnlyApi:
    def __init__(self, *, files=None, main=MAIN, head=HEAD, base=MAIN):
        self.files = files or [file("scripts/harmless_test.py", "added")]
        self.main, self.head, self.base = main, head, base
        self.paths = []

    def get(self, path):
        self.paths.append(path)
        if path == "/branches/main":
            return {"commit": {"sha": self.main}}
        if path == "/pulls/7":
            return {
                "number": 7, "state": "open", "draft": False,
                "head": {"sha": self.head},
                "base": {"sha": self.base, "ref": "main"},
                "changed_files": len(self.files),
            }
        if path == "/pulls/7/files?per_page=100&page=1":
            return self.files
        raise AssertionError(path)


def test_exact_head_main_and_pagination_audit_has_no_mutations():
    api = FakeReadOnlyApi()
    report = audit_pr(api, 7, HEAD, MAIN)
    assert report["checked_files"] == 1
    assert report["read_only"] is True
    assert report["authentic_match_verified"] is False
    assert report["exclusive_merge_lease"] is False
    assert all(not path.startswith("/pulls/7/merge") for path in api.paths)


def test_reject_stale_main_or_pr_head():
    for changes in ({"main": HEAD}, {"head": MAIN}, {"base": HEAD}):
        api = FakeReadOnlyApi(**changes)
        with pytest.raises(TrustBoundaryError):
            audit_pr(api, 7, HEAD, MAIN)


def test_realistic_step_name_bypass_requires_separate_source_check():
    # A compromised CI can still report all five "success" step names:
    # read-only audit must reject its modified ci.yml regardless of labels.
    fake_steps = [
        {"name": name, "conclusion": "success"}
        for name in ("Unit tests and PR evidence",
                     "Install pinned engine and verified patch",
                     "Confirm engine layout",
                     "Real full eight-seat simulated match",
                     "Preserve CI evidence")
    ]
    assert all(s["conclusion"] == "success" for s in fake_steps)
    api = FakeReadOnlyApi(files=[file(".github/workflows/ci.yml")])
    with pytest.raises(TrustBoundaryError, match="trusted full-match"):
        audit_pr(api, 7, HEAD, MAIN)
