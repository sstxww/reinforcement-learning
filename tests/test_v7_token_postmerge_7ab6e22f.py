"""Reproduce PR #185's GITHUB_TOKEN merge -> absent push-CI failure.
Loads the immutable reviewed script in an isolated runner, mocks GitHub;
this is neither a real merge nor a model strength test.
"""
import importlib.util
import os
import sys
from pathlib import Path
import pytest

BASE = "b"*40
HEAD = "a"*40
MERGED = "c"*40
REPO = "sstxww/reinforcement-learning"

def reviewed_module():
    p = os.environ.get("V7_REVIEW_TARGET")
    if not p or not Path(p).is_file():
        pytest.skip("Immutable review snapshot only present in session workflow")
    spec = importlib.util.spec_from_file_location("pr185_reviewed", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class MockGitHub:
    repo = REPO
    def __init__(self):
        self.merged = False
        self.polls = 0
        self.calls = []
    def call(self, path, method="GET", body=None):
        self.calls.append((path, method))
        if path == "/branches/main":
            return {"commit": {"sha": MERGED if self.merged else BASE}}
        if path == "/pulls/185":
            return {"number":185,"state":"open","draft":False,
                "base":{"ref":"main","sha":BASE},
                "head":{"sha":HEAD,"repo":{"full_name":REPO}},
                "mergeable":True,"mergeable_state":"clean",
                "user":{"login":"author"}}
        if path == "/pulls/185/reviews?per_page=100":
            return [{"user":{"login":"independent"},"state":"APPROVED",
                "commit_id":HEAD,"submitted_at":"2026-11-02T19:05:00Z"}]
        if path == "/commits/"+BASE:
            return {"commit":{"committer":{"date":"2026-11-02T19:00:00Z"}}}
        if path.startswith("/actions/runs?event=pull_request&head_sha="):
            return {"total_count":1,"workflow_runs":[{
                "id":7,"name":"CI - full-match gate","event":"pull_request",
                "head_sha":HEAD,"path":".github/workflows/ci.yml",
                "pull_requests":[{"number":185}],
                "status":"completed","conclusion":"success",
                "created_at":"2026-11-02T19:10:00Z",
                "run_started_at":"2026-11-02T19:10:00Z",
                "html_url":"https://github.com/sstxww/reinforcement-learning/actions/runs/7"}]}
        if path == "/actions/runs/7/jobs?per_page=100":
            names=("Unit tests and PR evidence","Install pinned engine and verified patch",
                   "Confirm engine layout","Real full eight-seat simulated match",
                   "Preserve CI evidence")
            return {"total_count":1,"jobs":[{"name":"tests-and-full-match",
                "conclusion":"success",
                "steps":[{"name":n,"conclusion":"success"} for n in names]}]}
        if path == "/pulls/185/merge" and method=="PUT":
            assert body=={"sha":HEAD,"merge_method":"squash"}
            self.merged=True
            return {"merged":True,"sha":MERGED}
        if path == "/actions/runs?event=push&branch=main&per_page=40":
            self.polls+=1
            return {"workflow_runs":[]}  # documented GITHUB_TOKEN behavior
        raise AssertionError("Unexpected mocked endpoint: "+path)

def test_pr185_merged_but_no_main_ci(monkeypatch):
    mod=reviewed_module()
    fake=MockGitHub()
    monkeypatch.setattr(mod,"GitHub",lambda repo,token:fake)
    monkeypatch.setattr(mod.time,"sleep",lambda seconds:None)
    monkeypatch.setattr(sys,"argv",["gate","--pr","185","--head",HEAD,
                                   "--main",BASE,"--apply"])
    for key,val in {"GITHUB_EVENT_NAME":"workflow_dispatch",
                    "GITHUB_REF":"refs/heads/main",
                    "GITHUB_REPOSITORY":REPO,
                    "GITHUB_TOKEN":"FAKE-TEST-ONLY"}.items():
        monkeypatch.setenv(key,val)
    with pytest.raises(mod.GateError,match="main CI still unverified"):
        mod.main()
    assert fake.merged and fake.polls==100
    assert not any("/dispatches" in path for path,_ in fake.calls)

def test_pr185_merge_job_cannot_dispatch_main_ci():
    p=os.environ.get("V7_REVIEW_WORKFLOW")
    if not p or not Path(p).is_file():
        pytest.skip("Immutable review workflow snapshot unavailable")
    s=Path(p).read_text(encoding="utf-8").split("  sha-bound-merge:",1)[1]
    assert "actions: read" in s
    assert "actions: write" not in s
    assert "GITHUB_TOKEN:" in s
