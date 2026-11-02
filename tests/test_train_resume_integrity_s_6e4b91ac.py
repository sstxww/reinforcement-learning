"""Offline regression checks for fail-closed PPO checkpoint lineage."""
import hashlib
import json
from pathlib import Path

import pytest
from tavern_ai.train import validate_resume_metadata


def fixture(tmp_path, *, schema=1, digest=True):
    archive = tmp_path / "model.zip"
    archive.write_bytes(b"isolated-test-fixture-not-a-PPO-model")
    engine = {"source_hash": "pinned", "actions": 245, "features": 4017, "cards": 447}
    meta = {"schema": schema, "engine": engine, "total_timesteps": 1280}
    if digest:
        meta["checkpoint_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".metadata.json").write_text(json.dumps(meta), encoding="utf-8")
    return archive, engine, meta


def test_valid_record_checks_digest_and_step_count(tmp_path):
    archive, engine, _ = fixture(tmp_path)
    result = validate_resume_metadata(archive, engine)
    assert result["total_timesteps"] == 1280
    assert len(result["checkpoint_sha256"]) == 64


def test_tampered_weights_fail_before_model_load(tmp_path):
    archive, engine, _ = fixture(tmp_path)
    archive.write_bytes(b"corrupted-checkpoint")
    with pytest.raises(ValueError, match="mismatch"):
        validate_resume_metadata(archive, engine)


@pytest.mark.parametrize("value", [0, -1, 3.5, True, "1280", None])
def test_invalid_cumulative_step_metadata_rejected(tmp_path, value):
    archive, engine, meta = fixture(tmp_path)
    meta["total_timesteps"] = value
    archive.with_suffix(".metadata.json").write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="timesteps"):
        validate_resume_metadata(archive, engine)


def test_unsupported_engine_is_rejected(tmp_path):
    archive, engine, _ = fixture(tmp_path)
    with pytest.raises(ValueError, match="engine"):
        validate_resume_metadata(archive, {**engine, "actions": 244})


def test_schema_two_requires_digest(tmp_path):
    archive, engine, _ = fixture(tmp_path, schema=2, digest=False)
    with pytest.raises(ValueError, match="requires SHA-256"):
        validate_resume_metadata(archive, engine)


def test_legacy_schema_one_remains_compatible_but_not_verified(tmp_path):
    archive, engine, _ = fixture(tmp_path, schema=1, digest=False)
    assert "checkpoint_sha256" not in validate_resume_metadata(archive, engine)


def test_missing_sidecar_is_rejected(tmp_path):
    path = tmp_path / "model.zip"
    path.write_bytes(b"abc")
    with pytest.raises(ValueError, match="Missing checkpoint"):
        validate_resume_metadata(path, {"version": "test"})
