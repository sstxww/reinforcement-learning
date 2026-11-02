"""Registry preflight is deliberately separate from executable recovery."""
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tavern_ai.contract import ENGINE_HASH, FEATURES, CARDS, ACTIONS
from tavern_ai.model_registry import load_registry, verify_release_bytes


def sample_registry(digest: str) -> dict:
    return {
        "schema": 1,
        "engine": {"version": "1.1.0", "source_hash": ENGINE_HASH,
                   "float_features": FEATURES, "card_slots": CARDS,
                   "action_count": ACTIONS},
        "best": None,
        "latest": {"id": "example", "checkpoint_sha256": digest},
        "candidates": [{"id": "example", "checkpoint_sha256": digest,
                        "training_steps": 128}],
    }


def save_registry(tmp_path, obj) -> dict:
    p = tmp_path / "registry.json"
    p.write_text(json.dumps(obj), encoding="utf-8")
    return load_registry(p)


def test_actual_selective_registry_is_coherent():
    p = Path(__file__).resolve().parents[1] / "models" / "registry.json"
    data = load_registry(p)
    assert data["best"] is None
    assert data["latest"]["training_steps"] == 1280


def test_preflight_reports_integrity_only(tmp_path):
    model = tmp_path / "model.zip"
    with zipfile.ZipFile(model, "w") as z:
        z.writestr("test-placeholder", "not an actual PPO model")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    registry = save_registry(tmp_path, sample_registry(digest))
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps({
        "engine": {"version": "1.1.0", "source_hash": ENGINE_HASH},
        "total_timesteps": 128, "checkpoint_sha256": digest,
    }), encoding="utf-8")
    out = verify_release_bytes(registry, "example", model, metadata)
    assert out["integrity_verified"] is True
    assert out["model_load_verified"] is False
    assert out["optimizer_resume_verified"] is False
    assert out["promoted_to_champion"] is False


def test_hash_mismatch_rejected(tmp_path):
    registry = save_registry(tmp_path, sample_registry("1" * 64))
    model = tmp_path / "model.zip"
    model.write_bytes(b"not the registered model")
    meta = tmp_path / "model.metadata.json"
    meta.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        verify_release_bytes(registry, "example", model, meta)


def test_corrupt_registry_and_promotion_rejected(tmp_path):
    base = sample_registry("2" * 64)
    base["best"] = "example"
    with pytest.raises(ValueError, match="Champion"):
        save_registry(tmp_path, base)
    base["best"] = None
    base["candidates"].append(dict(base["candidates"][0]))
    with pytest.raises(ValueError, match="Duplicate"):
        save_registry(tmp_path, base)
    base["candidates"].pop()
    base["engine"]["source_hash"] = "unknown"
    with pytest.raises(ValueError, match="contract mismatch"):
        save_registry(tmp_path, base)
