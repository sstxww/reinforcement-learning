"""Hermetic regression tests: synthetic ZIPs are never actual trained models."""
import hashlib
import json
import zipfile

import pytest

from tavern_ai.checkpoint_audit_ba09e2d4 import audit_checkpoint
from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES


def fixture_files(tmp_path, optimizer=True):
    model = tmp_path / "model.zip"
    metadata = tmp_path / "model.metadata.json"
    with zipfile.ZipFile(model, "w") as archive:
        archive.writestr("data", "{}")
        archive.writestr("policy.pth", "synthetic (not PyTorch weights)")
        if optimizer:
            archive.writestr("policy.optimizer.pth", "synthetic (not optimizer state)")
    info = {
        "schema": 1,
        "algorithm": "MaskablePPO",
        "total_timesteps": 1280,
        "training_seed": 42,
        "engine": {
            "version": "1.1.0", "source_hash": ENGINE_HASH,
            "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
            "n_cards": 3984,
        },
    }
    metadata.write_text(json.dumps(info), encoding="utf-8")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    return model, metadata, digest


def test_verified_archive_is_never_misreported_as_restored(tmp_path):
    model, meta, sha = fixture_files(tmp_path)
    result = audit_checkpoint(model, meta, sha)
    assert result["total_timesteps"] == 1280
    assert result["archive_and_optimizer_integrity_verified"] is True
    assert result["torch_load_verified"] is False
    assert result["resumable_training_verified"] is False
    assert result["real_game_verified"] is False
    assert result["champion_eligible"] is False


def test_wrong_or_unpinned_sha_rejected(tmp_path):
    model, meta, sha = fixture_files(tmp_path)
    with pytest.raises(ValueError, match="mismatch"):
        audit_checkpoint(model, meta, "0" * 64)
    with pytest.raises(ValueError, match="mandatory"):
        audit_checkpoint(model, meta, "")
    with pytest.raises(ValueError, match="mandatory"):
        audit_checkpoint(model, meta, sha.upper())


def test_missing_optimizer_rejected(tmp_path):
    model, meta, sha = fixture_files(tmp_path, optimizer=False)
    with pytest.raises(ValueError, match="optimizer"):
        audit_checkpoint(model, meta, sha)


@pytest.mark.parametrize("key,value", [
    ("source_hash", "different"),
    ("version", "2.0.0"),
    ("features", 4016),
    ("cards", 446),
    ("actions", 244),
])
def test_contract_mismatch_rejected(tmp_path, key, value):
    model, meta, sha = fixture_files(tmp_path)
    info = json.loads(meta.read_text())
    info["engine"][key] = value
    meta.write_text(json.dumps(info))
    with pytest.raises(ValueError, match="Incompatible"):
        audit_checkpoint(model, meta, sha)


def test_bad_metadata_rejected(tmp_path):
    model, meta, sha = fixture_files(tmp_path)
    info = json.loads(meta.read_text())
    info["total_timesteps"] = -1
    meta.write_text(json.dumps(info))
    with pytest.raises(ValueError, match="steps"):
        audit_checkpoint(model, meta, sha)


def test_corrupt_zip_rejected_without_hash_bypass(tmp_path):
    model, meta, sha = fixture_files(tmp_path)
    model.write_bytes(b"not a ZIP")
    changed = hashlib.sha256(model.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="archive"):
        audit_checkpoint(model, meta, changed)
    with pytest.raises(ValueError, match="mismatch"):
        audit_checkpoint(model, meta, sha)
