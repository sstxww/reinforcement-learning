"""Synthetic-only Release discovery regression: no real model claims."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "v5_release_discovery_ad1c30ff",
    Path(__file__).resolve().parents[1] / "scripts" / "v5_release_discovery_ad1c30ff.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _registry():
    return {
        "schema": 1,
        "repository": mod.REPO,
        "latest": {"id": "registered-1408"},
        "best": None,
        "champion": None,
        "candidates": [{"id": "registered-1408"}],
    }


def _release(i, name=None, assets=None, draft=False):
    return {
        "id": i, "tag_name": name or f"candidate-{i}",
        "draft": draft, "published_at": "2026-11-02T13:00:00Z",
        "assets": assets if assets is not None else [
            {"name": "model.zip"}, {"name": "model.metadata.json"}
        ],
    }


def test_pagination_reads_101_records_without_silent_truncation():
    calls = []
    def fetch(url):
        calls.append(url)
        page = int(url.rsplit("=", 1)[-1])
        return [_release(i) for i in range(100)] if page == 1 else [_release(100)]
    rows = mod.collect_releases(fetch)
    assert len(rows) == 101
    assert len(calls) == 2
    assert "page=2" in calls[-1]


def test_full_page_at_page_limit_fails_closed():
    with pytest.raises(RuntimeError, match="incomplete"):
        mod.collect_releases(lambda url: [_release(i) for i in range(100)], max_pages=1)


@pytest.mark.parametrize("page", [None, {}, [None], [_release(1), _release(1)]])
def test_malformed_or_duplicate_response_rejected(page):
    with pytest.raises((ValueError, RuntimeError)):
        mod.collect_releases(lambda url: page)


def test_registered_latest_is_not_replaced_by_new_unverified_release():
    result = mod.audit(_registry(), [
        _release(1, "registered-1408"),
        _release(2, "unregistered-1536"),
        _release(3, "rejected-1536", assets=[{"name": "model.zip"}]),
        _release(4, "draft-1536", draft=True),
    ])
    assert result["registered_latest"] == "registered-1408"
    assert result["registered_latest_public_release_exists"]
    assert result["unregistered_releases_with_weight_and_metadata_names"] == ["unregistered-1536"]
    assert result["champion_promotion_performed"] is False
    assert result["registry_mutated"] is False
    assert result["release_count_published"] == 3
    assert all(not x["promotion_eligible_by_this_audit"] for x in result["release_rows"])
    assert all(not x["bytes_verified_by_this_audit"] for x in result["release_rows"])


def test_missing_registered_release_is_visible():
    result = mod.audit(_registry(), [])
    assert result["registered_missing_from_remote_releases"] == ["registered-1408"]
    assert not result["registered_latest_public_release_exists"]


def test_duplicate_remote_tags_are_rejected():
    with pytest.raises(ValueError, match="Duplicate published Release tag"):
        mod.audit(_registry(), [_release(1, "same"), _release(2, "same")])


def test_duplicate_asset_names_rejected():
    with pytest.raises(ValueError, match="Duplicate asset"):
        mod.audit(_registry(), [_release(1, assets=[
            {"name": "model.zip"}, {"name": "model.zip"}, {"name": "model.metadata.json"}
        ])])


def test_unknown_registry_candidate_does_not_pass():
    doc = _registry()
    doc["latest"]["id"] = "not-in-registry"
    with pytest.raises(ValueError, match="Latest"):
        mod.audit(doc, [])


def test_remote_release_metadata_does_not_prove_checkpoint_resume():
    result = mod.audit(_registry(), [_release(5, "registered-1408")])
    row = result["release_rows"][0]
    assert row["registered"]
    assert row["has_weight_and_metadata_names"]
    assert not row["optimizer_resume_verified_by_this_audit"]
    assert not row["complete_raw_match_verified_by_this_audit"]
    assert not row["promotion_eligible_by_this_audit"]
