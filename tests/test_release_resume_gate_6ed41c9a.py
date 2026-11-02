"""Regression coverage for fail-closed, explicitly selected Release recovery."""
from __future__ import annotations

import hashlib
import json
import zipfile

import pytest

from tavern_ai.release_resume_gate_6ed41c9a import gate


TAG = "v5-test-durable-128"


def make_registry(tmp_path, digest, steps=128):
    url = "https://github.com/sstxww/reinforcement-learning/releases/tag/" + TAG
    data = {
        "schema": 1, "repository": "sstxww/reinforcement-learning",
        "engine": {"version": "1.1.0", "source_hash": "6d8712c93022ba11",
                   "float_features": 4017, "card_slots": 447, "action_count": 245},
        "best": None, "champion": None,
        "latest": {"id": TAG, "checkpoint_sha256": digest, "training_steps": steps,
                   "release": url, "release_tag": TAG, "model_asset": "model.zip",
                   "metadata_asset": "model.metadata.json", "promoted_to_best": False},
        "candidates": [{"id": TAG, "checkpoint_sha256": digest, "training_steps": steps,
                        "role": "candidate_unpromoted", "release_url": url}],
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def make_assets(tmp_path, steps=128):
    archive = tmp_path / "model.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("data", "{}")
        zf.writestr("policy.pth", b"checkpoint")
        zf.writestr("policy.optimizer.pth", b"optimizer")
    meta = {
        "schema": 1, "algorithm": "MaskablePPO", "total_timesteps": steps,
        "engine": {"version": "1.1.0", "source_hash": "6d8712c93022ba11",
                   "features": 4017, "cards": 447, "actions": 245, "n_cards": 3984},
    }
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps(meta), encoding="utf-8")
    return archive, metadata, hashlib.sha256(archive.read_bytes()).hexdigest()


def test_known_registered_tag_can_be_selected_without_claiming_resume(tmp_path):
    model, meta, digest = make_assets(tmp_path)
    reg = make_registry(tmp_path, digest)
    result = gate(reg, TAG)
    assert result["registry_checked"] is True
    assert result["downloaded_bytes_verified"] is False
    assert result["champion_promoted"] is False
    assert result["expected_sha256"] == digest


def test_real_bytes_are_checked_before_training_entrypoint(tmp_path):
    model, meta, digest = make_assets(tmp_path)
    reg = make_registry(tmp_path, digest)
    result = gate(reg, TAG, model, meta)
    assert result["downloaded_bytes_verified"] is True
    assert result["optimizer_resume"] == "pending_training_entrypoint"


@pytest.mark.parametrize("tag", ["", "../bad", "v5/bad", "bad tag", "$INJECTION", "unknown"])
def test_refuse_untrusted_or_unregistered_release(tmp_path, tag):
    model, meta, digest = make_assets(tmp_path)
    reg = make_registry(tmp_path, digest)
    with pytest.raises(ValueError):
        gate(reg, tag)


def test_refuse_modified_checkpoint(tmp_path):
    model, meta, digest = make_assets(tmp_path)
    reg = make_registry(tmp_path, digest)
    model.write_bytes(model.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="SHA256"):
        gate(reg, TAG, model, meta)


def test_refuse_mismatched_training_steps(tmp_path):
    model, meta, digest = make_assets(tmp_path, steps=128)
    reg = make_registry(tmp_path, digest, steps=256)
    with pytest.raises(ValueError, match="step mismatch"):
        gate(reg, TAG, model, meta)


def test_refuse_half_supplied_checkpoint_pair(tmp_path):
    model, meta, digest = make_assets(tmp_path)
    reg = make_registry(tmp_path, digest)
    with pytest.raises(ValueError, match="both"):
        gate(reg, TAG, model=model)


def test_refuse_fake_champion(tmp_path):
    model, meta, digest = make_assets(tmp_path)
    reg = make_registry(tmp_path, digest)
    data = json.loads(reg.read_text(encoding="utf-8"))
    data["champion"] = TAG
    reg.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="champion"):
        gate(reg, TAG)
