"""Fail-closed Release preflight regression tests; no downloaded weights needed."""
from __future__ import annotations

import hashlib
import json
import pytest

from tavern_ai.contract import (
    ACTIONS, CARDS, CATALOG_SHA256, ENGINE_HASH, FEATURES,
    PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT,
)
from tavern_ai.release_integrity import verify_source, audit_resume


def fixture(tmp_path):
    model = tmp_path / "model.zip"
    model.write_bytes(b"synthetic fixture only - NOT actual PPO weights")
    meta = {
        "schema": 2, "algorithm": "MaskablePPO", "total_timesteps": 1280,
        "engine": {
            "version": "1.1.0", "source_hash": ENGINE_HASH,
            "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
            "n_cards": 3984,
        },
        "checkpoint_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
    }
    meta["compatibility"] = {
        "engine": meta["engine"], "catalog_sha256": CATALOG_SHA256,
        "ruleset_id": RULESET_ID, "patch_sha256": PATCH_SHA256,
        "upstream_commit": UPSTREAM_COMMIT,
    }
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps(meta), encoding="utf-8")
    return model, metadata, meta


def check(model, metadata):
    return verify_source(
        model, metadata,
        hashlib.sha256(model.read_bytes()).hexdigest(),
        hashlib.sha256(metadata.read_bytes()).hexdigest(),
    )


def test_valid_metadata_schema_and_hash(tmp_path):
    model, metadata, _ = fixture(tmp_path)
    assert check(model, metadata)["total_timesteps"] == 1280


def test_reject_wrong_external_release_asset_hash(tmp_path):
    model, metadata, _ = fixture(tmp_path)
    with pytest.raises(ValueError, match="SHA256"):
        verify_source(model, metadata, "0" * 64, hashlib.sha256(metadata.read_bytes()).hexdigest())


@pytest.mark.parametrize("change", [
    {"schema": 1}, {"total_timesteps": 0}, {"total_timesteps": True},
    {"checkpoint_sha256": "f" * 64}, {"algorithm": "PPO"},
])
def test_reject_incompatible_metadata(tmp_path, change):
    model, metadata, data = fixture(tmp_path)
    data.update(change)
    metadata.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        check(model, metadata)


@pytest.mark.parametrize("field", [
    "catalog_sha256", "patch_sha256", "upstream_commit", "ruleset_id",
])
def test_reject_catalog_or_patch_mismatch(tmp_path, field):
    model, metadata, data = fixture(tmp_path)
    data["compatibility"][field] = "incompatible"
    metadata.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="compatibility mismatch"):
        check(model, metadata)


def test_reject_engine_layout_and_vocab_mismatch(tmp_path):
    model, metadata, data = fixture(tmp_path)
    data["engine"]["cards"] = 124
    metadata.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="engine mismatch"):
        check(model, metadata)


def test_exact_bounded_resume_budget(tmp_path):
    model, metadata, _ = fixture(tmp_path)
    with pytest.raises(ValueError, match="exactly 128"):
        audit_resume(
            model, metadata, "0" * 64, "0" * 64,
            tmp_path / "out.zip", tmp_path / "audit.json", steps=4096,
        )


def test_missing_source_never_starts_fresh(tmp_path):
    with pytest.raises(FileNotFoundError):
        verify_source(tmp_path / "absent.zip", tmp_path / "absent.json", "0" * 64, "0" * 64)
