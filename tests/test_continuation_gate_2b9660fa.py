"""Synthetic-only regression tests; not a trained model or real-game receipt."""
import hashlib
import json
import zipfile

import pytest

from tavern_ai.continuation_gate import inspect_continuation
from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES


def fixture_pair(tmp_path):
    weights = tmp_path / "model.zip"
    with zipfile.ZipFile(weights, "w") as archive:
        archive.writestr("data", "{}")
        archive.writestr("policy.pth", b"synthetic test-only")
        archive.writestr("policy.optimizer.pth", b"synthetic test-only")
    metadata = tmp_path / "model.metadata.json"
    sha = hashlib.sha256(weights.read_bytes()).hexdigest()
    metadata.write_text(json.dumps({
        "schema": 1, "algorithm": "MaskablePPO",
        "total_timesteps": 128,
        "checkpoint_sha256": sha,
        "engine": {"version": "1.1.0", "source_hash": ENGINE_HASH,
                   "features": FEATURES, "cards": CARDS,
                   "actions": ACTIONS, "n_cards": 3984},
    }), encoding="utf-8")
    return weights, metadata, sha


def test_no_checkpoint_must_explicitly_opt_into_fresh_start(tmp_path):
    model = tmp_path / "model.zip"
    metadata = tmp_path / "model.metadata.json"
    with pytest.raises(ValueError, match="explicit fresh-start"):
        inspect_continuation(model, metadata)
    report = inspect_continuation(model, metadata, allow_fresh_start=True)
    assert report["mode"] == "fresh_explicit"
    assert report["model_strength_verified"] is False


def test_partial_artifact_fails_even_when_fresh_start_allowed(tmp_path):
    model = tmp_path / "model.zip"
    metadata = tmp_path / "model.metadata.json"
    model.write_bytes(b"partial")
    with pytest.raises(ValueError, match="Incomplete checkpoint"):
        inspect_continuation(model, metadata, allow_fresh_start=True)


def test_verified_archive_not_mistaken_for_verified_optimizer_resume(tmp_path):
    weights, metadata, sha = fixture_pair(tmp_path)
    report = inspect_continuation(weights, metadata, expected_sha256=sha)
    assert report["mode"] == "resume_verified_archive"
    assert report["archive_integrity"] == "passed"
    assert report["provenance_out_of_band"] is True
    assert report["total_timesteps"] == 128
    assert report["optimizer_resume_verified"] is False
    assert report["model_strength_verified"] is False


def test_tampered_weights_refused_before_model_load(tmp_path):
    weights, metadata, sha = fixture_pair(tmp_path)
    with weights.open("ab") as f:
        f.write(b"tampered")
    with pytest.raises(ValueError, match="SHA256"):
        inspect_continuation(weights, metadata, expected_sha256=sha)


def test_wrong_trusted_digest_refused(tmp_path):
    weights, metadata, _ = fixture_pair(tmp_path)
    with pytest.raises(ValueError, match="Trusted Release SHA256"):
        inspect_continuation(weights, metadata, expected_sha256="f" * 64)


def test_missing_legacy_digest_refused(tmp_path):
    weights, metadata, _ = fixture_pair(tmp_path)
    obj = json.loads(metadata.read_text())
    obj.pop("checkpoint_sha256")
    metadata.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(ValueError, match="no recorded SHA256"):
        inspect_continuation(weights, metadata)


def test_engine_contract_or_algorithm_mismatch_refused(tmp_path):
    weights, metadata, _ = fixture_pair(tmp_path)
    obj = json.loads(metadata.read_text())
    obj["engine"]["actions"] = 246
    metadata.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(ValueError, match="contract"):
        inspect_continuation(weights, metadata)


def test_missing_optimizer_component_refused(tmp_path):
    weights, metadata, _ = fixture_pair(tmp_path)
    with zipfile.ZipFile(weights, "w") as archive:
        archive.writestr("data", "{}")
        archive.writestr("policy.pth", "not a usable PPO")
    obj = json.loads(metadata.read_text())
    obj["checkpoint_sha256"] = hashlib.sha256(weights.read_bytes()).hexdigest()
    metadata.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(ValueError, match="optimizer"):
        inspect_continuation(weights, metadata)
