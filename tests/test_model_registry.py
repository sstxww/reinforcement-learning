"""Offline integrity checks. These are not a substitute for an actual PPO reload."""
from __future__ import annotations

import hashlib
import json
import zipfile

import pytest

from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES
from tavern_ai.model_registry import read_registry, verify_archive


def fixture(tmp_path):
    checkpoint = tmp_path / "checkpoint.zip"
    with zipfile.ZipFile(checkpoint, "w") as archive:
        for name in ("data", "policy.pth", "policy.optimizer.pth"):
            archive.writestr(name, b"test-only")
    entry = {
        "model_id": "test-1", "sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        "status": "Unverified", "engine_source_hash": ENGINE_HASH,
        "release_url": "https://github.com/sstxww/reinforcement-learning/releases/tag/test-1",
        "training_steps": 128, "load_verified": False, "resume_verified": False,
        "full_game_verified": False, "paired_eval_verified": False,
    }
    metadata = tmp_path / "checkpoint.metadata.json"
    metadata.write_text(json.dumps({"schema": 1, "algorithm": "MaskablePPO",
        "total_timesteps": 128, "engine": {
            "version": "1.1.0", "source_hash": ENGINE_HASH,
            "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
        }}), encoding="utf-8")
    return checkpoint, metadata, entry


def test_real_registry_structure():
    assert read_registry(__import__("pathlib").Path("models/registry.json"))["champion_id"] is None


def test_preflight_accepts_valid_archive(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path)
    result = verify_archive(entry, checkpoint, metadata)
    assert result["optimizer_member_present"] is True
    assert result["load_or_resume_verified"] is False


def test_rejects_sha_mismatch(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path)
    entry["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="SHA256"):
        verify_archive(entry, checkpoint, metadata)


def test_rejects_incompatible_card_schema(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path)
    payload = json.loads(metadata.read_text())
    payload["engine"]["cards"] = CARDS - 1
    metadata.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="Engine"):
        verify_archive(entry, checkpoint, metadata)


def test_rejects_missing_optimizer(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path)
    with zipfile.ZipFile(checkpoint, "w") as archive:
        archive.writestr("data", b"test-only")
        archive.writestr("policy.pth", b"test-only")
    entry["sha256"] = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="optimizer"):
        verify_archive(entry, checkpoint, metadata)


def test_never_invents_champion(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path)
    entry["status"] = "Champion"
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"schema": 1, "champion_id": "test-1", "models": [entry]}))
    with pytest.raises(ValueError, match="gates"):
        read_registry(path)


def test_duplicate_ids_are_rejected(tmp_path):
    _, _, entry = fixture(tmp_path)
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"schema": 1, "champion_id": None,
                                "models": [entry, dict(entry)]}))
    with pytest.raises(ValueError, match="Duplicate"):
        read_registry(path)


def test_schema2_actual_release_format(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path)
    payload = json.loads(metadata.read_text())
    from tavern_ai.contract import CATALOG_SHA256, RULESET_ID, PATCH_SHA256, UPSTREAM_COMMIT
    payload["schema"] = 2
    payload["checkpoint_sha256"] = entry["sha256"]
    payload["compatibility"] = {
        "engine": payload["engine"], "catalog_sha256": CATALOG_SHA256,
        "ruleset_id": RULESET_ID, "patch_sha256": PATCH_SHA256,
        "upstream_commit": UPSTREAM_COMMIT,
    }
    metadata.write_text(json.dumps(payload))
    assert verify_archive(entry, checkpoint, metadata)["status"] == "integrity_preflight_passed"
    payload["compatibility"]["catalog_sha256"] = "incorrect"
    metadata.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="catalog"):
        verify_archive(entry, checkpoint, metadata)


def test_schema2_embedded_sha_must_match_release(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path)
    payload = json.loads(metadata.read_text())
    from tavern_ai.contract import CATALOG_SHA256, RULESET_ID, PATCH_SHA256, UPSTREAM_COMMIT
    payload["schema"] = 2
    payload["checkpoint_sha256"] = "0" * 64
    payload["compatibility"] = {
        "engine": payload["engine"], "catalog_sha256": CATALOG_SHA256,
        "ruleset_id": RULESET_ID, "patch_sha256": PATCH_SHA256,
        "upstream_commit": UPSTREAM_COMMIT,
    }
    metadata.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="Embedded"):
        verify_archive(entry, checkpoint, metadata)
