"""Regression tests for fail-closed V5 Release inventory and local archive auditing."""
import copy
import hashlib
import json
from pathlib import Path

import pytest
from tavern_ai.checkpoint_registry_68099929 import load_registry, verify_local_release

ROOT = Path(__file__).resolve().parents[1]


def test_real_registry_is_conservative_and_has_complete_api_inventory():
    r = load_registry(ROOT / "models/registry.json")
    assert r["best"] is None
    assert r["latest"]["release_tag"] == "v2-learning-41413557445"
    assert r["latest"]["training_steps"] == 1280
    assert len(r["github_release_asset_inventory"]) == 6
    assert all(x["binary_download_hash_checked_in_this_integration"] is False
               for x in r["github_release_asset_inventory"])


def fixture_files(tmp_path):
    r = copy.deepcopy(load_registry(ROOT / "models/registry.json"))
    tag = "test-private-checkpoint"
    data = b"fake model bytes only for checksum regression"
    model = tmp_path / "model.zip"
    model.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    r["github_release_asset_inventory"] = [
        {"tag": tag,
         "model_asset": {"name": "model.zip", "bytes": len(data),
                         "github_api_sha256": "sha256:" + digest},
         "metadata_asset_present": True}
    ]
    engine = {"version": "1.1.0", "source_hash": "6d8712c93022ba11",
              "features": 4017, "cards": 447, "actions": 245, "n_cards": 3984}
    meta = {"checkpoint_sha256": digest, "engine": engine,
            "compatibility": {"engine": engine}, "total_timesteps": 256}
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps(meta), encoding="utf-8")
    return r, tag, model, metadata


def test_valid_binary_and_metadata_are_verified_without_claiming_resume(tmp_path):
    r, tag, model, metadata = fixture_files(tmp_path)
    report = verify_local_release(r, tag, model, metadata)
    assert report["binary_sha256_verified"] is True
    assert report["training_steps"] == 256
    assert report["model_load_tested"] is False
    assert report["resume_training_tested"] is False
    assert report["champion_promoted"] is False


def test_tampered_binary_is_rejected(tmp_path):
    r, tag, model, metadata = fixture_files(tmp_path)
    model.write_bytes(model.read_bytes() + b"tamper")
    with pytest.raises(ValueError, match="checksum"):
        verify_local_release(r, tag, model, metadata)


def test_wrong_metadata_hash_is_rejected(tmp_path):
    r, tag, model, metadata = fixture_files(tmp_path)
    meta = json.loads(metadata.read_text())
    meta["checkpoint_sha256"] = "0" * 64
    metadata.write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="Metadata checkpoint"):
        verify_local_release(r, tag, model, metadata)


def test_wrong_observation_layout_is_rejected(tmp_path):
    r, tag, model, metadata = fixture_files(tmp_path)
    meta = json.loads(metadata.read_text())
    meta["engine"]["cards"] = 124
    meta["compatibility"]["engine"]["cards"] = 124
    metadata.write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="engine layout"):
        verify_local_release(r, tag, model, metadata)


def test_duplicate_release_tags_are_rejected(tmp_path):
    r, _, _, _ = fixture_files(tmp_path)
    r["github_release_asset_inventory"].append(copy.deepcopy(r["github_release_asset_inventory"][0]))
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(r), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_registry(path)
