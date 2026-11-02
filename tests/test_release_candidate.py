"""No network or training required to verify the model registry and checkpoint gate."""
import hashlib
import json

import pytest

from scripts.verify_release_candidate import read_registry, verify_checkpoint


@pytest.fixture
def sample(tmp_path):
    p = tmp_path / "registry.json"
    data = {
        "schema": 1, "repository": "sstxww/reinforcement-learning",
        "engine": {"name": "TavernGym", "version": "1.1.0", "source_hash": "6d8712c93022ba11",
            "observation": "observe2", "float_features": 4017, "card_slots": 447, "action_count": 245},
        "best": None, "champion": None, "latest": {"id": "test-v1"},
        "candidates": [{"id": "test-v1", "checkpoint_sha256": hashlib.sha256(b"model bytes").hexdigest(),
                       "training_steps": 128}],
    }
    p.write_text(json.dumps(data))
    return p, data


def test_read_existing_main_style_registry(sample):
    path, _ = sample
    assert read_registry(path)["latest"]["id"] == "test-v1"


def test_rejects_unproven_best(sample):
    path, data = sample
    data["best"] = "test-v1"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Champion"):
        read_registry(path)


def test_rejects_wrong_engine(sample):
    path, data = sample
    data["engine"]["action_count"] = 244
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="contract"):
        read_registry(path)


def test_rejects_corrupt_registry_sha(sample):
    path, data = sample
    data["candidates"][0]["checkpoint_sha256"] = "bad"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="SHA256"):
        read_registry(path)


def test_rejects_duplicate_ids(sample):
    path, data = sample
    data["candidates"].append(dict(data["candidates"][0]))
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Duplicate"):
        read_registry(path)


def test_metadata_and_bytes_are_bound(sample, tmp_path):
    path, _ = sample
    registry = read_registry(path)
    model = tmp_path / "model.zip"
    model.write_bytes(b"model bytes")
    metadata = tmp_path / "model.metadata.json"
    meta = {"total_timesteps": 128, "engine": {"version": "1.1.0",
           "source_hash": "6d8712c93022ba11", "features": 4017,
           "cards": 447, "actions": 245}}
    metadata.write_text(json.dumps(meta))
    assert verify_checkpoint(model, metadata, registry, "test-v1")["release_bytes_verified"]
    model.write_bytes(b"tampered bytes")
    with pytest.raises(ValueError, match="SHA256"):
        verify_checkpoint(model, metadata, registry, "test-v1")


def test_invalid_steps_rejected(sample, tmp_path):
    path, _ = sample
    registry = read_registry(path)
    model = tmp_path / "model.zip"
    model.write_bytes(b"model bytes")
    metadata = tmp_path / "model.metadata.json"
    meta = {"total_timesteps": 129, "engine": {"version": "1.1.0",
           "source_hash": "6d8712c93022ba11", "features": 4017,
           "cards": 447, "actions": 245}}
    metadata.write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="lineage"):
        verify_checkpoint(model, metadata, registry, "test-v1")
