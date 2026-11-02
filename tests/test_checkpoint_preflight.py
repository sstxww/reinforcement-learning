"""All ZIP fixtures below are synthetic; no model or match evidence is claimed."""
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tavern_ai.checkpoint_preflight import audit_archive
from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES


def make_fixture(tmp_path, **changes):
    model = tmp_path / "model.zip"
    with zipfile.ZipFile(model, "w") as zf:
        for name in ("data", "policy.pth", "policy.optimizer.pth"):
            zf.writestr(name, b"synthetic-unit-test-only")
    meta = {
        "schema": 1, "algorithm": "MaskablePPO", "total_timesteps": 256,
        "engine": {"version": "1.1.0", "source_hash": ENGINE_HASH,
                   "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
                   "n_cards": 4096},
    }
    meta.update(changes)
    path = tmp_path / "model.metadata.json"
    path.write_text(json.dumps(meta), encoding="utf-8")
    return model, path, hashlib.sha256(model.read_bytes()).hexdigest()


def test_synthetic_preflight_is_not_promotion(tmp_path):
    model, meta, digest = make_fixture(tmp_path)
    result = audit_archive(model, meta, digest)
    assert result["archive_integrity"] == "passed"
    assert result["model_load"] == "not_tested"
    assert result["optimizer_resume"] == "not_tested"
    assert result["champion_eligible"] is False


def test_rejects_modified_weights(tmp_path):
    model, meta, digest = make_fixture(tmp_path)
    with model.open("ab") as handle:
        handle.write(b"tampered")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        audit_archive(model, meta, digest)


def test_rejects_unknown_digest_and_missing_files(tmp_path):
    model, meta, digest = make_fixture(tmp_path)
    with pytest.raises(ValueError, match="64-hex"):
        audit_archive(model, meta, "unverified")
    with pytest.raises(FileNotFoundError):
        audit_archive(model, tmp_path / "missing.json", digest)


@pytest.mark.parametrize("change", [
    {"total_timesteps": True},
    {"total_timesteps": 0},
    {"algorithm": "PPO"},
    {"schema": 2},
    {"engine": {"version": "1.1.0", "source_hash": "wrong",
                "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
                "n_cards": 4096}},
    {"engine": {"version": "1.1.0", "source_hash": ENGINE_HASH,
                "features": FEATURES, "cards": CARDS, "actions": 244,
                "n_cards": 4096}},
])
def test_rejects_bad_metadata(tmp_path, change):
    model, meta, digest = make_fixture(tmp_path, **change)
    with pytest.raises(ValueError):
        audit_archive(model, meta, digest)


def test_rejects_missing_optimizer_even_with_correct_digest(tmp_path):
    model, meta, _ = make_fixture(tmp_path)
    with zipfile.ZipFile(model, "w") as zf:
        zf.writestr("data", "unit test")
        zf.writestr("policy.pth", "unit test")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="optimizer"):
        audit_archive(model, meta, digest)


def test_rejects_non_zip_even_with_correct_digest(tmp_path):
    model, meta, _ = make_fixture(tmp_path)
    model.write_bytes(b"not-a-model")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="ZIP"):
        audit_archive(model, meta, digest)
