"""Regression coverage for authoritative main model Release ledger (#87)."""
import copy
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tavern_ai.model_registry import load_registry, validate_registry, verify_asset


def index() -> dict:
    return json.loads(Path("models/registry.json").read_text(encoding="utf-8"))


def test_main_registry_unpromoted_and_latest_ref_consistent():
    data, entries = load_registry(Path("models/registry.json"))
    assert data["champion"] is None
    assert data["best"] is None
    assert data["latest"]["id"] == "v2-learning-41413557445"
    assert entries[data["latest"]["id"]]["training_steps"] == 1280
    assert all(e["role"] == "candidate_unpromoted" for e in entries.values())


def test_tampered_sha_and_duplicate_ids_rejected():
    data = index()
    data["candidates"][0]["checkpoint_sha256"] = "bad"
    with pytest.raises(ValueError, match="SHA256"):
        validate_registry(data)
    data = index()
    data["candidates"].append(copy.deepcopy(data["candidates"][0]))
    with pytest.raises(ValueError, match="Duplicate"):
        validate_registry(data)


def test_engine_and_champion_fail_closed():
    data = index()
    data["engine"]["action_count"] = 244
    with pytest.raises(ValueError, match="Engine"):
        validate_registry(data)
    data = index()
    data["champion"] = data["latest"]["id"]
    with pytest.raises(ValueError, match="Champion"):
        validate_registry(data)
    data = index()
    data["best"] = data["latest"]
    with pytest.raises(ValueError, match="Best"):
        validate_registry(data)


def test_invalid_latest_pointer_and_bad_parent_rejected():
    data = index()
    data["latest"]["checkpoint_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="Latest pointer"):
        validate_registry(data)
    data = index()
    data["candidates"][-1]["source_release"] = "nonexistent-source"
    with pytest.raises(ValueError, match="parent"):
        validate_registry(data)
    data = index()
    data["candidates"][-1]["source_release"] = data["candidates"][0]["id"]
    data["candidates"][-1]["training_steps"] = 128
    with pytest.raises(ValueError, match="Parent"):
        validate_registry(data)


def test_sha_and_zip_integrity(tmp_path):
    target = tmp_path / "model.zip"
    with zipfile.ZipFile(target, "w") as z:
        z.writestr("data", "fictional fixture; not a PPO model")
    entry = {"id": "fixture-only", "checkpoint_sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
    result = verify_asset(entry, target)
    assert result["integrity"] == "sha256_and_zip_ok"
    assert result["load_and_optimizer_resume_verified_by_this_check"] is False
    with target.open("ab") as f:
        f.write(b"tampered")
    with pytest.raises(ValueError, match="SHA256"):
        verify_asset(entry, target)


def test_correct_hash_does_not_allow_invalid_zip(tmp_path):
    target = tmp_path / "model.zip"
    target.write_bytes(b"not a zip")
    entry = {"id": "fixture-only", "checkpoint_sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
    with pytest.raises(ValueError, match="ZIP"):
        verify_asset(entry, target)
