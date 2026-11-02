"""Offline regression tests for explicit, fail-closed V5 Release selection."""
import copy
import json
from pathlib import Path

import pytest

from scripts.v5_train_release_source_1e55e01e import select_source


@pytest.fixture
def registry():
    return json.loads(Path("models/registry.json").read_text(encoding="utf-8"))


def test_default_is_canonical_latest_unpromoted_release(registry):
    chosen = select_source(registry)
    assert chosen["model_id"] == registry["latest"]["id"]
    assert chosen["release_tag"] == registry["latest"]["release_tag"]
    assert chosen["expected_sha256"] == registry["latest"]["checkpoint_sha256"]
    assert chosen["expected_steps"] == registry["latest"]["training_steps"]
    assert chosen["source_is_verified_for_resume"] is False


def test_explicit_registered_release_only(registry):
    candidate = registry["candidates"][0]
    chosen = select_source(registry, candidate["id"])
    assert chosen["model_id"] == candidate["id"]
    assert chosen["expected_sha256"] == candidate["checkpoint_sha256"]


@pytest.mark.parametrize("candidate", ["", "unknown-release", "../model.zip",
                                         "v5-main-rogue"])
def test_unknown_models_never_fall_back_to_random_weights(registry, candidate):
    if candidate:
        with pytest.raises(ValueError, match="Unregistered"):
            select_source(registry, candidate)


def test_corrupt_canonical_registry_fails(registry):
    bad = copy.deepcopy(registry)
    bad["latest"]["checkpoint_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        select_source(bad)


def test_missing_model_digest_fails(registry):
    bad = copy.deepcopy(registry)
    ident = bad["latest"]["id"]
    next(x for x in bad["candidates"] if x["id"] == ident)["checkpoint_sha256"] = None
    with pytest.raises(ValueError):
        select_source(bad)


def test_modified_model_release_url_fails(registry):
    bad = copy.deepcopy(registry)
    ident = bad["latest"]["id"]
    next(x for x in bad["candidates"] if x["id"] == ident)["release_url"] = "https://example.com/model"
    with pytest.raises(ValueError):
        select_source(bad)

def test_metadata_digest_is_provided_from_index(registry):
    index = json.loads(Path("models/release_asset_digests.json").read_text(encoding="utf-8"))
    selected = select_source(registry, asset_index=index)
    row = next(x for x in index["assets"] if x["id"] == selected["model_id"])
    assert selected["metadata_sha256"] == row["metadata"]["sha256"]


def test_missing_indexed_metadata_digest_fails_closed(registry):
    index = json.loads(Path("models/release_asset_digests.json").read_text(encoding="utf-8"))
    row = next(x for x in index["assets"] if x["id"] == registry["latest"]["id"])
    row["metadata"]["sha256"] = None
    with pytest.raises(ValueError, match="metadata digest"):
        select_source(registry, asset_index=index)


def test_indexed_weight_digest_must_match_canonical_registry(registry):
    index = json.loads(Path("models/release_asset_digests.json").read_text(encoding="utf-8"))
    row = next(x for x in index["assets"] if x["id"] == registry["latest"]["id"])
    row["weights"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="weight digest"):
        select_source(registry, asset_index=index)


def test_indexed_metadata_url_cannot_point_to_other_model(registry):
    index = json.loads(Path("models/release_asset_digests.json").read_text(encoding="utf-8"))
    row = next(x for x in index["assets"] if x["id"] == registry["latest"]["id"])
    row["metadata"]["url"] = "https://example.org/metadata.json"
    with pytest.raises(ValueError, match="asset URLs"):
        select_source(registry, asset_index=index)
