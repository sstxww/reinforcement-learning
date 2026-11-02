"""Offline exact-ref claim and failure-injection tests."""
import json
import pytest
from scripts.v7_task_claim_d494b86e import ClaimError, ClaimExists, claim_ref, acquire, request

BASE = "c5edec2e3261dacdf3908796ebfe0457fb76c02e"
TREE = "b" * 40
NEW_TREE = "c" * 40
NEW_COMMIT = "d" * 40
TASK = "coordination/atomic-claim-v1"
SESSION = "s-20261103-d494b86e"

class Fake:
    def __init__(self, exists=False, mismatch=False):
        self.calls = []
        self.exists = exists
        self.mismatch = mismatch
    def __call__(self, token, method, path, body=None):
        assert token == "mock-token"
        self.calls.append((method, path, body))
        if method == "GET" and "/git/commits/" in path:
            return {"tree": {"sha": TREE}}
        if method == "POST" and path.endswith("/git/trees"):
            return {"sha": NEW_TREE}
        if method == "POST" and path.endswith("/git/commits"):
            return {"sha": NEW_COMMIT}
        if method == "POST" and path.endswith("/git/refs"):
            if self.exists: raise ClaimExists("existing")
            return {"ref": body["ref"], "object": {"sha": NEW_COMMIT}}
        if method == "GET" and "/git/ref/" in path:
            return {"ref": claim_ref(TASK),
                    "object": {"sha": BASE if self.mismatch else NEW_COMMIT}}
        raise AssertionError((method, path))

def test_atomic_create_contains_owner_and_no_patch():
    api = Fake()
    result = acquire("sstxww/reinforcement-learning", TASK, SESSION, BASE,
                     "mock-token", api)
    assert result["claimed"] and not result["merge_lease"]
    assert len(api.calls) == 5
    m = json.loads(api.calls[1][2]["tree"][0]["content"])
    assert m["session_id"] == SESSION and m["task_key"] == TASK
    assert m["base_main_sha"] == BASE
    assert m["kind"] == "one_shot_task_claim_not_merge_lease"
    assert api.calls[2][2]["parents"] == [BASE]
    assert api.calls[3][2] == {"ref": claim_ref(TASK), "sha": NEW_COMMIT}
    assert all(method != "PATCH" for method, _, _ in api.calls)

def test_raced_ref_creation_does_not_take_over():
    api = Fake(exists=True)
    with pytest.raises(ClaimExists):
        acquire("sstxww/reinforcement-learning", TASK, SESSION, BASE,
                "mock-token", api)
    assert len(api.calls) == 4

def test_unexpected_readback_fails_closed():
    with pytest.raises(ClaimError, match="readback"):
        acquire("sstxww/reinforcement-learning", TASK, SESSION, BASE,
                "mock-token", Fake(mismatch=True))

def test_hash_preserves_full_task_namespace():
    assert claim_ref(TASK) == claim_ref(TASK)
    assert claim_ref("coordination/a-b") != claim_ref("coordination/a_b")
    for bad in ("", "A/B", "../unsafe", "abc//def", "abc/", "a", "abc def"):
        with pytest.raises(ValueError): claim_ref(bad)

@pytest.mark.parametrize("repo,session,sha", [
    ("unscoped", SESSION, BASE),
    ("owner/repo", "invalid-session", BASE),
    ("owner/repo", SESSION, "main"),
    ("owner/repo?x", SESSION, BASE),
])
def test_invalid_input_makes_no_api_call(repo, session, sha):
    api = Fake()
    with pytest.raises(ValueError):
        acquire(repo, TASK, session, sha, "mock-token", api)
    assert not api.calls

def test_missing_base_tree_rejects_before_new_ref():
    def api(token, method, path, body=None):
        assert method == "GET"
        return {"tree": {"sha": "INVALID"}}
    with pytest.raises(ClaimError, match="Base tree"):
        acquire("owner/repo", TASK, SESSION, BASE, "mock-token", api)

def test_missing_token_fails_before_network():
    with pytest.raises(ClaimError, match="required"):
        request("", "GET", "repos/x/y/git/refs")
