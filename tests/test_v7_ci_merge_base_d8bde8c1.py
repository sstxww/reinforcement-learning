"""Synthetic mutation tests, NOT real games or GitHub merge authorization."""
from copy import deepcopy
import pytest

from scripts.v7_ci_merge_base_d8bde8c1 import (
    MergeBaseEvidenceError, verify_ci_merge_base
)

HEAD = "a" * 40
MAIN = "b" * 40
OLD_MAIN = "c" * 40


def run():
    return {
        "id": 15, "event": "pull_request", "name": "CI - full-match gate",
        "path": ".github/workflows/ci.yml", "head_sha": HEAD,
        "created_at": "2026-11-02T19:30:00Z",
        "run_started_at": "2026-11-02T19:50:00Z",
        "status": "completed", "conclusion": "success",
        "pull_requests": [{"number": 42, "head": {"sha": HEAD},
                           "base": {"ref": "main", "sha": MAIN}}],
    }


def verify(payload):
    return verify_ci_merge_base(payload, pr_number=42, head_sha=HEAD, main_sha=MAIN)


def test_exact_head_and_base_positive():
    result = verify(run())
    assert result["base_bound"] is True
    assert result["merge_authorized"] is False
    assert result["tested_main_sha"] == MAIN


def test_stale_queued_ci_run_rejected_even_if_started_after_main_change():
    payload = run()
    payload["pull_requests"][0]["base"]["sha"] = OLD_MAIN
    # Deliberately late run_started_at cannot repair a stale synthetic merge base.
    with pytest.raises(MergeBaseEvidenceError, match="STALE_BASE"):
        verify(payload)


@pytest.mark.parametrize("mutation", [
    lambda p: p.update(pull_requests=[]),
    lambda p: p.update(pull_requests=[p["pull_requests"][0]] * 2),
    lambda p: p["pull_requests"][0].update(number=43),
    lambda p: p["pull_requests"][0]["head"].update(sha=OLD_MAIN),
    lambda p: p["pull_requests"][0]["base"].update(ref="other"),
    lambda p: p["pull_requests"][0]["base"].pop("sha"),
    lambda p: p.update(conclusion="failure"),
    lambda p: p.update(status="in_progress"),
    lambda p: p.update(head_sha=OLD_MAIN),
    lambda p: p.update(event="push"),
    lambda p: p.update(name="Other workflow"),
    lambda p: p.update(path=".github/workflows/other.yml"),
])
def test_malformed_or_unrelated_run_rejected(mutation):
    payload = deepcopy(run())
    mutation(payload)
    with pytest.raises(MergeBaseEvidenceError):
        verify(payload)


def test_missing_provenance_and_invalid_expected_sha_rejected():
    payload = run()
    payload.pop("pull_requests")
    with pytest.raises(MergeBaseEvidenceError):
        verify(payload)
    with pytest.raises(MergeBaseEvidenceError):
        verify_ci_merge_base(run(), pr_number=42, head_sha="short", main_sha=MAIN)
    with pytest.raises(MergeBaseEvidenceError):
        verify_ci_merge_base(run(), pr_number=42, head_sha=HEAD, main_sha="bad")
