"""Read-only ZIP/metadata preflight, using only synthetic ZIPs for unit tests."""
import copy
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tavern_ai.release_preflight_490e3c78 import verify_release_pair


ROOT = Path(__file__).resolve().parents[1]


def get_registry() -> dict:
    return json.loads((ROOT / "models" / "registry.json").read_text("utf-8"))


def fixture(tmp_path, *, include_optimizer=True):
    path = tmp_path / "model.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("data", "{}")
        archive.writestr("policy.pth", "synthetic, NOT real torch weights")
        if include_optimizer:
            archive.writestr("policy.optimizer.pth", "synthetic optimizer entry")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    registry = copy.deepcopy(get_registry())
    model_id = registry["latest"]["id"]
    registry["latest"]["checkpoint_sha256"] = digest
    for row in registry["candidates"]:
        if row["id"] == model_id:
            row["checkpoint_sha256"] = digest
            break
    metadata = tmp_path / "model.metadata.json"
    expected = registry["engine"]
    metadata.write_text(json.dumps({
        "engine": {"version": expected["version"],
                   "source_hash": expected["source_hash"],
                   "features": expected["float_features"],
                   "cards": expected["card_slots"],
                   "actions": expected["action_count"]},
        "total_timesteps": registry["latest"]["training_steps"],
        "checkpoint_sha256": digest, "algorithm": "MaskablePPO"
    }), encoding="utf-8")
    return registry, model_id, path, metadata


def test_preflight_verifies_bytes_and_not_executable_recovery(tmp_path):
    registry, model_id, path, metadata = fixture(tmp_path)
    result = verify_release_pair(registry, model_id, path, metadata)
    assert result["zip_crc_verified"] is True
    assert result["optimizer_archive_entry_present"] is True
    assert result["torch_model_loaded"] is False
    assert result["optimizer_restored"] is False
    assert result["ppo_steps_executed"] == 0
    assert result["champion_promoted"] is False


def test_missing_optimizer_state_rejected(tmp_path):
    registry, model_id, path, metadata = fixture(tmp_path, include_optimizer=False)
    with pytest.raises(ValueError, match="optimizer"):
        verify_release_pair(registry, model_id, path, metadata)


def test_metadata_steps_mismatch_rejected(tmp_path):
    registry, model_id, path, metadata = fixture(tmp_path)
    content = json.loads(metadata.read_text())
    content["total_timesteps"] = 999999
    metadata.write_text(json.dumps(content))
    with pytest.raises(ValueError, match="train steps"):
        verify_release_pair(registry, model_id, path, metadata)


def test_metadata_engine_and_zip_hash_mismatch_rejected(tmp_path):
    registry, model_id, path, metadata = fixture(tmp_path)
    info = json.loads(metadata.read_text())
    info["engine"]["actions"] = 246
    metadata.write_text(json.dumps(info))
    with pytest.raises(ValueError, match="engine mismatch"):
        verify_release_pair(registry, model_id, path, metadata)
    path.write_bytes(path.read_bytes() + b"tampering")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        verify_release_pair(registry, model_id, path, metadata)


def test_unknown_model_is_rejected(tmp_path):
    registry, _, path, metadata = fixture(tmp_path)
    with pytest.raises(ValueError, match="Unknown"):
        verify_release_pair(registry, "made-up-model", path, metadata)
