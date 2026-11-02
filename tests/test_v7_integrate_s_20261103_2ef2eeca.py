"""Synthetic offline fixtures only; NOT TavernGym match receipts."""
import importlib.util
from pathlib import Path

import pytest

FILE = Path(__file__).resolve().parents[1] / "scripts" / "v7_integrate.py"
spec = importlib.util.spec_from_file_location("v7_integrate", FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

HEAD, BASE = "a" * 40, "b" * 40


class FakeAPI:
    def __init__(self):
        self.pr = {
            "state": "open", "draft": False, "mergeable": True,
            "mergeable_state": "clean",
            "head": {"sha": HEAD}, "base": {"sha": BASE, "ref": "main"},
            "requested_reviewers": [], "requested_teams": [], "merged": False,
        }
        self.main_sha = BASE
        self.run = {
            "id": 73, "head_sha": HEAD, "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/proj/actions/runs/73",
            "pull_requests": [
                {"number": 12, "head": {"sha": HEAD}, "base": {"sha": BASE}}
            ],
        }
        self.steps = [
            {"name": name, "conclusion": "success"}
            for name in module.REQUIRED_STEPS
        ]
        self.artifacts = [
            {"name": "ci-full-match-73", "expired": False, "size_in_bytes": 900}
        ]
        self.calls = []

    def request(self, path, *, method="GET", body=None):
        self.calls.append((method, path, body))
        if path == "/branches/main":
            return {"commit": {"sha": self.main_sha}}
        if path == "/pulls/12":
            return self.pr
        if path.startswith("/pulls/12/reviews"):
            return []
        if path.startswith("/actions/workflows/ci.yml/runs"):
            return {"workflow_runs": [self.run]}
        if path == "/actions/runs/73/jobs?per_page=100":
            return {"jobs": [{
                "name": "tests-and-full-match", "status": "completed",
                "conclusion": "success", "steps": self.steps
            }]}
        if path == "/actions/runs/73/artifacts?per_page=100":
            return {"artifacts": self.artifacts}
        if path == "/pulls/12/merge" and method == "PUT":
            assert body["sha"] == HEAD
            self.pr["merged"] = True
            self.main_sha = "c" * 40
            return {"merged": True, "sha": self.main_sha}
        raise AssertionError((path, method))


def call(api, merge=False):
    return module.run(api, pr_number=12, head_sha=HEAD,
                      main_sha=BASE, merge=merge)


def test_good_preflight_never_mutates():
    fake = FakeAPI()
    result = call(fake)
    assert result["status"] == "preflight_only"
    assert not any(method != "GET" for method, _, _ in fake.calls)


def test_conditional_merge_rechecks_and_records_new_main():
    fake = FakeAPI()
    result = call(fake, merge=True)
    assert result["status"] == "merged_main_ci_pending"
    assert result["merge_sha"] == "c" * 40
    assert len([c for c in fake.calls if c[0] == "PUT"]) == 1


def test_stale_main_fails_before_any_mutation():
    fake = FakeAPI()
    fake.main_sha = "e" * 40
    with pytest.raises(module.GateError, match="main advanced"):
        call(fake, merge=True)
    assert not any(c[0] == "PUT" for c in fake.calls)


def test_draft_and_head_changes_fail():
    for change in ({"draft": True},
                   {"head": {"sha": "f" * 40}},
                   {"mergeable_state": "dirty"}):
        fake = FakeAPI()
        fake.pr.update(change)
        with pytest.raises(module.GateError):
            call(fake, merge=True)


def test_ci_must_match_exact_base_and_head():
    fake = FakeAPI()
    fake.run["pull_requests"][0]["base"]["sha"] = "f" * 40
    with pytest.raises(module.GateError, match="no successful full-match CI"):
        call(fake)


def test_incomplete_engine_or_match_not_green():
    fake = FakeAPI()
    fake.steps = [
        s for s in fake.steps
        if s["name"] != "Real full eight-seat simulated match"
    ]
    with pytest.raises(module.GateError, match="job steps"):
        call(fake)


def test_absent_artifact_is_blocker():
    fake = FakeAPI()
    fake.artifacts = []
    with pytest.raises(module.GateError, match="artifact absent"):
        call(fake)


def test_sha_and_repo_validation():
    with pytest.raises(module.GateError, match="expected PR head"):
        module.inspect(FakeAPI(), pr_number=12,
                       head_sha="not-a-sha", main_sha=BASE)
    with pytest.raises(module.GateError, match="invalid repository"):
        module.GitHubAPI("../evil", "token")
