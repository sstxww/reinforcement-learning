"""Offline regression checks for strict and non-promotional Release provenance."""
import copy
import hashlib
import json

import pytest

from scripts.verify_release_candidate import read_registry, verify_checkpoint


@pytest.fixture
def registry(tmp_path):
    data = {
        "schema": 1, "repository": "sstxww/reinforcement-learning",
        "engine": {"version": "1.1.0", "source_hash": "6d8712c93022ba11",
                   "features": 4017, "cards": 447, "actions": 245},
        "champion": None, "latest_candidate": "unit-test",
        "checkpoints": [{"id": "unit-test", "role": "challenger",
                         "release_tag": "unit-test", "model_asset": "model.zip",
                         "metadata_asset": "model.metadata.json",
                         "sha256": hashlib.sha256(b"test model").hexdigest(),
                         "steps": 128, "parent": None}],
    }
    f = tmp_path / "registry.json"
    f.write_text(json.dumps(data))
    return f, data


def test_valid_registry(registry):
    f, _ = registry
    assert read_registry(f)["champion"] is None


def test_disallow_forged_champion(registry):
    f, data = registry
    data["champion"] = "unit-test"
    f.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Champion"):
        read_registry(f)


def test_disallow_invalid_digest(registry):
    f, data = registry
    data["checkpoints"][0]["sha256"] = "x" * 64
    f.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Invalid"):
        read_registry(f)


def test_checkpoint_hash_and_metadata(registry, tmp_path):
    f, data = registry
    model = tmp_path / "model.zip"
    model.write_bytes(b"test model")
    meta = tmp_path / "model.metadata.json"
    metadata = {"total_timesteps": 128,
                "engine": {"version": "1.1.0", "source_hash": "6d8712c93022ba11",
                           "features": 4017, "cards": 447, "actions": 245}}
    meta.write_text(json.dumps(metadata))
    assert verify_checkpoint(model, meta, read_registry(f), "unit-test")["byte_integrity_verified"]
    model.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="SHA256"):
        verify_checkpoint(model, meta, read_registry(f), "unit-test")


def test_reject_mismatched_steps(registry, tmp_path):
    f, _ = registry
    model = tmp_path / "model.zip"
    model.write_bytes(b"test model")
    meta = tmp_path / "model.metadata.json"
    meta.write_text(json.dumps({"total_timesteps": 129,
        "engine": {"version": "1.1.0", "source_hash": "6d8712c93022ba11",
                   "features": 4017, "cards": 447, "actions": 245}}))
    with pytest.raises(ValueError, match="lineage"):
        verify_checkpoint(model, meta, read_registry(f), "unit-test")
