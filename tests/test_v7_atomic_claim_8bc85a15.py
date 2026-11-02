"""Offline regression tests for the V7 task-claim CAS; no GitHub writes or simulator."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts/v7_atomic_claim_8bc85a15.py"
spec = importlib.util.spec_from_file_location("v7_claim", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
A = "s-20261103-8bc85a15"
B = "s-20261103-aaaaaaaa"
NA = "a" * 32
NB = "b" * 32
TASK = "coordination-atomic-claim-cli"


class FakeGitHub:
    def __init__(self):
        self.commits = {"main-sha": {"message": "main", "tree": {"sha": "tree-0"}, "parents": []}}
        self.refs = {"refs/heads/main": "main-sha"}
        self.serial = 0
        self.before_patch = None

    def __call__(self, method, path, payload=None):
        suffix = path.split("/repos/sstxww/reinforcement-learning/", 1)[1]
        if method == "GET" and suffix.startswith("git/ref/"):
            key = "refs/" + suffix[len("git/ref/"):]
            if key not in self.refs:
                raise mod.ApiError(404, "Not found")
            return {"object": {"sha": self.refs[key]}, "ref": key}
        if method == "GET" and suffix.startswith("git/commits/"):
            return self.commits[suffix.split("/")[-1]]
        if method == "POST" and suffix == "git/commits":
            parent = payload["parents"][0]
            assert parent in self.commits
            self.serial += 1
            sha = hashlib.sha256(f"{self.serial}:{parent}:{payload['message']}".encode()).hexdigest()
            self.commits[sha] = {"message": payload["message"],
                                 "tree": {"sha": payload["tree"]},
                                 "parents": [parent]}
            return {"sha": sha}
        if method == "POST" and suffix == "git/refs":
            ref = payload["ref"]
            if ref in self.refs:
                raise mod.ApiError(422, "Already exists")
            self.refs[ref] = payload["sha"]
            return {"ref": ref}
        if method == "PATCH" and suffix.startswith("git/refs/"):
            key = "refs/" + suffix[len("git/refs/"):]
            if self.before_patch is not None:
                fn, self.before_patch = self.before_patch, None
                fn(key)
            desired = payload["sha"]
            assert payload["force"] is False
            if self.commits[desired]["parents"] != [self.refs[key]]:
                raise mod.ApiError(422, "Update is not a fast forward")
            self.refs[key] = desired
            return {"object": {"sha": desired}}
        raise AssertionError((method, suffix))


def test_claim_is_exclusive_and_reusable_after_authorized_release():
    api = FakeGitHub()
    first = mod.transition(api, mod.REPO, TASK, A, NA, "acquire")
    assert first == api.refs[mod.slug_path(TASK)]
    with pytest.raises(mod.ClaimError, match="already held"):
        mod.transition(api, mod.REPO, TASK, B, NB, "acquire")
    with pytest.raises(mod.ClaimError, match="exact verified owner"):
        mod.transition(api, mod.REPO, TASK, A, NB, "release")
    released = mod.transition(api, mod.REPO, TASK, A, NA, "release")
    assert released != first
    claimed = mod.transition(api, mod.REPO, TASK, B, NB, "acquire")
    assert claimed == api.refs[mod.slug_path(TASK)]
    assert mod.decode(api.commits[claimed]["message"], TASK)["owner"] == B


def test_concurrent_acquire_from_same_parent_cannot_both_win():
    api = FakeGitHub()
    mod.ensure_claim_ref(api, mod.REPO, TASK)
    def competitor(key):
        parent = api.refs[key]
        sha = api("POST", "/repos/sstxww/reinforcement-learning/git/commits", {
            "message": mod.encode(TASK, B, NB, "held"), "tree": "tree-0", "parents": [parent]})["sha"]
        api.refs[key] = sha
    api.before_patch = competitor
    with pytest.raises(mod.ClaimError, match="lost a race"):
        mod.transition(api, mod.REPO, TASK, A, NA, "acquire")
    assert mod.decode(api.commits[api.refs[mod.slug_path(TASK)]]["message"], TASK)["owner"] == B


def test_unknown_ref_state_fails_closed_and_no_force_reset():
    api = FakeGitHub()
    api.refs[mod.slug_path(TASK)] = "main-sha"
    with pytest.raises(mod.ClaimError, match="Unknown claim ref"):
        mod.transition(api, mod.REPO, TASK, A, NA, "acquire")
    assert api.refs[mod.slug_path(TASK)] == "main-sha"


def test_reject_invalid_slug_session_nonce_and_repo():
    api = FakeGitHub()
    for bad in ("ab", "UPPER", "../main", "bad/branch"):
        with pytest.raises(mod.ClaimError):
            mod.transition(api, mod.REPO, bad, A, NA, "acquire")
    with pytest.raises(mod.ClaimError):
        mod.transition(api, mod.REPO, TASK, "random-user", NA, "acquire")
    with pytest.raises(mod.ClaimError):
        mod.transition(api, mod.REPO, TASK, A, "bad-nonce", "acquire")
    with pytest.raises(mod.ClaimError):
        mod.transition(api, "other/repo", TASK, A, NA, "acquire")


def test_reject_unexpected_claim_schema():
    with pytest.raises(mod.ClaimError):
        mod.decode(mod.PREFIX + json.dumps({"schema": 9}), TASK)
