"""Independent synthetic mutation tests; NOT real game or CI receipts."""
import importlib.util
from pathlib import Path
import copy
import pytest

src = Path(__file__).resolve().parents[1] / "scripts" / "v7_serial_merge_gate_c5853eb8.py"
spec = importlib.util.spec_from_file_location("v7_serial_merge_gate_c5853eb8", src)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

SHA = "a"*40
MAIN = "b"*40
REPO = "sstxww/reinforcement-learning"


def good():
    pr = {"number": 42, "state": "open", "draft": False,
          "base": {"ref": "main", "sha": MAIN},
          "head": {"sha": SHA, "repo": {"full_name": REPO}},
          "mergeable": True, "mergeable_state": "clean",
          "user": {"login": "author"}}
    ref = {"object": {"sha": MAIN}}
    ci = {"name": "CI - full-match gate", "event": "pull_request",
          "status": "completed", "conclusion": "success", "head_sha": SHA,
          "pull_requests": [{"number": 42}], "html_url": "https://example.test/run/10"}
    jobs = {"jobs": [{"name": "tests-and-full-match", "conclusion": "success",
                      "steps": [{"name": "Unit tests and PR evidence", "conclusion": "success"},
                                {"name": "Real full eight-seat simulated match", "conclusion": "success"}]}]}
    reviews = [{"user": {"login": "reviewer"}, "state": "APPROVED", "commit_id": SHA}]
    return pr, ref, ci, jobs, reviews


def check(parts):
    return gate.validate(*parts, repo=REPO, number=42, head=SHA, main=MAIN)


def test_exact_good_independent_review_and_ci():
    result = check(good())
    assert result["safe_for_serial_review"] is True
    assert result["main_before"] == MAIN


@pytest.mark.parametrize("change", [
    lambda v: v[0]["base"].update(ref="agent/stacked"),
    lambda v: v[0]["head"].update(sha="c"*40),
    lambda v: v[0].update(draft=True),
    lambda v: v[0].update(mergeable=None),
    lambda v: v[0].update(mergeable_state="unstable"),
    lambda v: v[1]["object"].update(sha="c"*40),
    lambda v: v[2].update(conclusion="failure"),
    lambda v: v[2].update(head_sha="c"*40),
    lambda v: v[2].update(pull_requests=[{"number": 41}]),
    lambda v: v[3]["jobs"][0]["steps"][1].update(conclusion="failure"),
    lambda v: v[4][0].update(commit_id="c"*40),
    lambda v: v[4][0].update(state="CHANGES_REQUESTED"),
    lambda v: v[4][0]["user"].update(login="author"),
])
def test_fail_closed_mutations(change):
    v = list(copy.deepcopy(good()))
    change(v)
    with pytest.raises(gate.GateError):
        check(v)


def test_synthetic_merge_sha_allowed_only_if_pr_head_is_pinned():
    v = list(good())
    v[2]["head_sha"] = "c"*40
    v[2]["pull_requests"] = [{"number": 42, "head": {"sha": SHA}}]
    assert check(v)["safe_for_serial_review"]


def test_later_review_supersedes_old_approval():
    v = list(good())
    v[4].append({"user": {"login": "reviewer"}, "state": "CHANGES_REQUESTED",
                 "commit_id": SHA})
    with pytest.raises(gate.GateError):
        check(v)
