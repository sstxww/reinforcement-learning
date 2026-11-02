"""Pure, fast regression tests for Release registry invariants."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from tavern_ai.checkpoint_registry import file_sha256, validate_registry, verify_release

REGISTRY = Path("models/registry.json")


def inventory():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_real_release_inventory_is_pessimistic():
    data = validate_registry(inventory())
    assert data["champion_id"] is None
    assert data["latest_resumable_id"] is None
    assert data["entries"][0]["role"] == "unverified"
    assert data["entries"][0]["verification"]["resume"] is False


def test_rejects_duplicate_id_and_nonrelease_url():
    data = inventory()
    data["entries"].append(copy.deepcopy(data["entries"][0]))
    with pytest.raises(ValueError, match="Duplicate"):
        validate_registry(data)
    data = inventory()
    data["entries"][0]["release_url"] = "https://example.com/model.zip"
    with pytest.raises(ValueError, match="Release"):
        validate_registry(data)


def test_unverified_model_cannot_be_champion_or_latest():
    data = inventory()
    model_id = data["entries"][0]["model_id"]
    data["champion_id"] = model_id
    data["entries"][0]["role"] = "champion"
    with pytest.raises(ValueError, match="verification"):
        validate_registry(data)
    data = inventory()
    data["latest_resumable_id"] = model_id
    with pytest.raises(ValueError, match="not verified resumable"):
        validate_registry(data)


def test_rejects_invalid_digest_and_step_fields():
    data = inventory()
    data["entries"][0]["model_sha256"] = "0"
    with pytest.raises(ValueError, match="digest"):
        validate_registry(data)
    data = inventory()
    data["entries"][0]["training_steps"] = True
    with pytest.raises(ValueError, match="training steps"):
        validate_registry(data)


def test_local_file_hash_and_metadata_fail_closed(tmp_path):
    model = tmp_path / "model.zip"
    model.write_bytes(b"immutable test weight bytes")
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps({
        "algorithm": "MaskablePPO", "total_timesteps": 1280,
        "engine": {"source_hash": "6d8712c93022ba11"},
    }), encoding="utf-8")
    record = copy.deepcopy(inventory()["entries"][0])
    record["model_sha256"] = hashlib.sha256(model.read_bytes()).hexdigest()
    assert file_sha256(model) == record["model_sha256"]
    report = verify_release(record, model, metadata, cpu_smoke=False)
    assert report["hash_verified"] is True
    assert report["cpu_load_verified"] is False
    assert report["resume_verified"] is False
    assert report["champion_promoted"] is False

    model.write_bytes(b"tampered bytes")
    with pytest.raises(ValueError, match="SHA256"):
        verify_release(record, model, metadata)
    model.write_bytes(b"immutable test weight bytes")
    metadata.write_text(json.dumps({
        "algorithm": "MaskablePPO", "total_timesteps": 1281,
        "engine": {"source_hash": "6d8712c93022ba11"},
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="step"):
        verify_release(record, model, metadata)


def test_missing_files_are_not_reported_as_success(tmp_path):
    record = inventory()["entries"][0]
    with pytest.raises(FileNotFoundError):
        verify_release(record, tmp_path / "missing.zip", tmp_path / "missing.json")
