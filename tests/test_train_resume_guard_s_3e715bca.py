"""Offline preflight regressions. Synthetic ZIPs are NEVER real PPO models."""
import hashlib
import json
import zipfile

import pytest

from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES
from tavern_ai.train import inspect_resume, sha256_file


def fixture(tmp_path, *, with_hash=True, with_optimizer=True):
    archive = tmp_path / "model.zip"
    names = ["data", "policy.pth"]
    if with_optimizer:
        names.append("policy.optimizer.pth")
    with zipfile.ZipFile(archive, "w") as zf:
        for name in names:
            zf.writestr(name, b"synthetic-test-bytes-only")
    engine = {"version": "1.1.0", "source_hash": ENGINE_HASH,
              "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
              "n_cards": 3983}
    metadata = {"schema": 1, "algorithm": "MaskablePPO",
                "engine": engine, "total_timesteps": 256}
    if with_hash:
        metadata["checkpoint_sha256"] = sha256_file(archive)
    meta_path = tmp_path / "model.metadata.json"
    meta_path.write_text(json.dumps(metadata), encoding="utf-8")
    return archive, meta_path, engine


def test_integrity_preflight_accepts_consistent_synthetic_archive(tmp_path):
    archive, metadata, engine = fixture(tmp_path)
    assert inspect_resume(archive, engine)["total_timesteps"] == 256
    assert inspect_resume(archive, engine, sha256_file(archive))["algorithm"] == "MaskablePPO"


def test_rejects_changed_weights_before_ppo_load(tmp_path):
    archive, metadata, engine = fixture(tmp_path)
    archive.write_bytes(archive.read_bytes() + b"tampering")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        inspect_resume(archive, engine)


def test_rejects_wrong_independent_release_digest(tmp_path):
    archive, metadata, engine = fixture(tmp_path)
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        inspect_resume(archive, engine, "0" * 64)


def test_rejects_missing_optimizer_even_when_metadata_digest_matches(tmp_path):
    archive, metadata, engine = fixture(tmp_path, with_optimizer=False)
    with pytest.raises(ValueError, match="optimizer"):
        inspect_resume(archive, engine)


def test_rejects_incompatible_metadata_or_step_counter(tmp_path):
    archive, metadata, engine = fixture(tmp_path)
    bad_engine = dict(engine, actions=244)
    with pytest.raises(ValueError, match="vocabulary"):
        inspect_resume(archive, bad_engine)
    obj = json.loads(metadata.read_text(encoding="utf-8"))
    obj["total_timesteps"] = True
    metadata.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(ValueError, match="total_timesteps"):
        inspect_resume(archive, engine)


def test_legacy_model_without_embedded_digest_receives_structural_audit(tmp_path):
    archive, metadata, engine = fixture(tmp_path, with_hash=False)
    assert inspect_resume(archive, engine)["total_timesteps"] == 256
    archive.write_bytes(b"not a real SB3 zip")
    with pytest.raises(ValueError, match="ZIP"):
        inspect_resume(archive, engine)


def test_missing_metadata_or_weights_fail_closed(tmp_path):
    archive, metadata, engine = fixture(tmp_path)
    metadata.unlink()
    with pytest.raises(ValueError, match="Missing checkpoint"):
        inspect_resume(archive, engine)
    archive.unlink()
    with pytest.raises(FileNotFoundError):
        inspect_resume(archive, engine)
