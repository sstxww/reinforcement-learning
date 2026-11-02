"""Synthetic failure-injection tests: these are NOT match receipts or training evidence."""
import hashlib
import json
from pathlib import Path

import pytest

from tavern_ai.recovery_v5_6f4c8a19 import audit_release, sha256_file


ENGINE = {"version": "1.1.0", "source_hash": "6d8712c93022ba11",
          "features": 4017, "cards": 447, "actions": 245}


def fixture_files(tmp_path: Path):
    model = tmp_path / "model.zip"
    model.write_bytes(b"synthetic bytes, not a real PPO checkpoint")
    registry = tmp_path / "registry.json"
    meta = tmp_path / "model.metadata.json"
    entry = {"id": "synthetic", "role": "challenger", "promotion_verified": False,
             "sha256": sha256_file(model), "training_steps": 1280, "engine": ENGINE,
             "release_tag": "synthetic-only", "source_commit": "test"}
    registry.write_text(json.dumps({"schema": 1, "champion": None,
                                    "candidates": [entry]}), encoding="utf-8")
    meta.write_text(json.dumps({"schema": 1, "algorithm": "MaskablePPO",
                                "total_timesteps": 1280, "engine": ENGINE}), encoding="utf-8")
    return registry, model, meta


def test_verification_does_not_claim_champion(tmp_path):
    registry, model, metadata = fixture_files(tmp_path)
    result = audit_release(registry, "synthetic", model, metadata)
    assert result["status"] == "file_and_metadata_verified"
    assert result["eligible_for_champion"] is False
    assert result["optimizer_state"] == "not_tested"
    assert result["sha256"] == hashlib.sha256(model.read_bytes()).hexdigest()


def test_tampered_model_fails_closed(tmp_path):
    registry, model, metadata = fixture_files(tmp_path)
    model.write_bytes(b"changed")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        audit_release(registry, "synthetic", model, metadata)


def test_engine_mismatch_fails_closed(tmp_path):
    registry, model, metadata = fixture_files(tmp_path)
    parsed = json.loads(metadata.read_text())
    parsed["engine"]["cards"] = 124
    metadata.write_text(json.dumps(parsed))
    with pytest.raises(ValueError, match="engine mismatch"):
        audit_release(registry, "synthetic", model, metadata)


def test_steps_mismatch_fails_closed(tmp_path):
    registry, model, metadata = fixture_files(tmp_path)
    parsed = json.loads(metadata.read_text())
    parsed["total_timesteps"] = 999
    metadata.write_text(json.dumps(parsed))
    with pytest.raises(ValueError, match="Training step"):
        audit_release(registry, "synthetic", model, metadata)


def test_ambiguous_or_promoted_entry_fails_closed(tmp_path):
    registry, model, metadata = fixture_files(tmp_path)
    parsed = json.loads(registry.read_text())
    parsed["candidates"].append(parsed["candidates"][0])
    registry.write_text(json.dumps(parsed))
    with pytest.raises(ValueError, match="exactly one"):
        audit_release(registry, "synthetic", model, metadata)
    parsed["candidates"].pop()
    parsed["champion"] = "synthetic"
    registry.write_text(json.dumps(parsed))
    with pytest.raises(ValueError, match="Champion"):
        audit_release(registry, "synthetic", model, metadata)
