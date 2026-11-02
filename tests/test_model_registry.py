"""Integrity regression tests are offline; full TavernGym match runs in CI."""
import copy
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tavern_ai.model_registry import load_registry, validate_registry, verify_asset


def index() -> dict:
    return json.loads(Path("models/registry.json").read_text(encoding="utf-8"))


def test_real_registry_is_explicitly_unpromoted_and_historical():
    data, entries = load_registry(Path("models/registry.json"))
    assert data["champion"] is None
    assert data["latest"] == "v2-learning-41413557445"
    assert entries[data["latest"]]["steps"] == 1280
    assert entries[data["latest"]]["release_resume_verified"] is False
    assert all(e["status"] == "challenger" for e in entries.values())


def test_tampered_sha_and_duplicate_ids_rejected():
    data = index()
    data["models"][0]["sha256"] = "bad"
    with pytest.raises(ValueError, match="SHA256"):
        validate_registry(data)
    data = index()
    data["models"].append(copy.deepcopy(data["models"][0]))
    with pytest.raises(ValueError, match="Duplicate"):
        validate_registry(data)


def test_engine_and_champion_fail_closed():
    data = index()
    data["engine"]["actions"] = 244
    with pytest.raises(ValueError, match="Engine"):
        validate_registry(data)
    data = index()
    data["champion"] = data["latest"]
    with pytest.raises(ValueError, match="Champion"):
        validate_registry(data)


def test_missing_parent_or_invalid_history_rejected():
    data = index()
    data["models"][-1]["parent"] = "ghost"
    with pytest.raises(ValueError, match="parent"):
        validate_registry(data)
    data = index()
    data["models"][-1]["steps"] = 128
    with pytest.raises(ValueError, match="Parent"):
        validate_registry(data)


def test_sha_and_zip_integrity(tmp_path):
    target = tmp_path / "model.zip"
    with zipfile.ZipFile(target, "w") as z:
        z.writestr("data", "test model artifact (not a real PPO model)")
    content = target.read_bytes()
    entry = {"id": "fixture-only", "sha256": hashlib.sha256(content).hexdigest()}
    result = verify_asset(entry, target)
    assert result["integrity"] == "sha256_and_zip_ok"
    assert result["load_and_optimizer_resume_verified_by_this_check"] is False
    with target.open("ab") as f:
        f.write(b"tampered")
    with pytest.raises(ValueError, match="SHA256"):
        verify_asset(entry, target)


def test_valid_hash_is_not_enough_when_not_zip(tmp_path):
    target = tmp_path / "model.zip"
    target.write_bytes(b"not a zip")
    entry = {"id": "fixture-only", "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
    with pytest.raises(ValueError, match="ZIP"):
        verify_asset(entry, target)
