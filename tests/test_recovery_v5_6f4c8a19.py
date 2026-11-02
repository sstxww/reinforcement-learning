"""Synthetic failure-injection tests: these are NOT match receipts or training evidence."""
import hashlib
import json
from pathlib import Path

import pytest

from tavern_ai.recovery_v5_6f4c8a19 import audit_release, sha256_file
from tavern_ai.contract import CATALOG_SHA256, PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT


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


def fixture_schema2(registry, model, metadata):
    parsed = json.loads(metadata.read_text())
    parsed["schema"] = 2
    parsed["checkpoint_sha256"] = sha256_file(model)
    parsed["engine"]["n_cards"] = 3984
    parsed["compatibility"] = {
        "engine": dict(parsed["engine"]),
        "catalog_sha256": CATALOG_SHA256,
        "ruleset_id": RULESET_ID,
        "patch_sha256": PATCH_SHA256,
        "upstream_commit": UPSTREAM_COMMIT,
    }
    metadata.write_text(json.dumps(parsed), encoding="utf-8")
    return parsed


def test_real_v2_schema_shape_accepts_full_compatibility(tmp_path):
    registry, model, metadata = fixture_files(tmp_path)
    fixture_schema2(registry, model, metadata)
    result = audit_release(registry, "synthetic", model, metadata)
    assert result["metadata_schema"] == 2
    assert result["v2_compatibility_verified"] is True
    assert result["eligible_for_champion"] is False


def test_v2_embedded_hash_tampering_rejected(tmp_path):
    registry, model, metadata = fixture_files(tmp_path)
    parsed = fixture_schema2(registry, model, metadata)
    parsed["checkpoint_sha256"] = "0" * 64
    metadata.write_text(json.dumps(parsed))
    with pytest.raises(ValueError, match="embedded checkpoint SHA256 mismatch"):
        audit_release(registry, "synthetic", model, metadata)


def test_v2_catalog_mismatch_rejected(tmp_path):
    registry, model, metadata = fixture_files(tmp_path)
    parsed = fixture_schema2(registry, model, metadata)
    parsed["compatibility"]["catalog_sha256"] = "f" * 64
    metadata.write_text(json.dumps(parsed))
    with pytest.raises(ValueError, match="compatibility fingerprint mismatch"):
        audit_release(registry, "synthetic", model, metadata)


def test_v2_engine_vocabulary_mismatch_rejected(tmp_path):
    registry, model, metadata = fixture_files(tmp_path)
    parsed = fixture_schema2(registry, model, metadata)
    parsed["engine"]["n_cards"] = 124
    parsed["compatibility"]["engine"]["n_cards"] = 124
    metadata.write_text(json.dumps(parsed))
    with pytest.raises(ValueError, match="card vocabulary mismatch"):
        audit_release(registry, "synthetic", model, metadata)
