"""Offline tests: synthetic ZIPs are NOT actual TavernGym/model receipts."""
import hashlib
import json
import zipfile

import pytest

from tavern_ai.model_registry import read_registry, verify_local
from tavern_ai.contract import ENGINE_HASH, FEATURES, CARDS, ACTIONS


def make_case(tmp_path, *, optimizer=True, source_hash=ENGINE_HASH, steps=128):
    archive = tmp_path / "model.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("data", "{}")
        z.writestr("policy.pth", b"synthetic-test-only")
        if optimizer:
            z.writestr("policy.optimizer.pth", b"synthetic-test-only")
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps({
        "schema": 1, "algorithm": "MaskablePPO", "total_timesteps": steps,
        "engine": {"version": "1.1.0", "source_hash": source_hash,
                   "features": FEATURES, "cards": CARDS, "actions": ACTIONS}
    }), encoding="utf-8")
    entry = {"id": "test", "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
             "reported_total_timesteps": 128}
    return entry, archive, metadata


def test_good_archive_and_metadata_verify_without_claiming_real_load(tmp_path):
    entry, archive, metadata = make_case(tmp_path)
    report = verify_local(entry, archive, metadata)
    assert report["hash_verified"] is True
    assert report["optimizer_state_present"] is True
    assert report["resume_test_verified"] is False
    assert report["full_match_verified"] is False
    assert report["strength_gain_verified"] is False
    assert report["cpu_load_verified"] is False


def test_hash_tampering_is_rejected(tmp_path):
    entry, archive, metadata = make_case(tmp_path)
    with archive.open("ab") as f:
        f.write(b"tampering")
    with pytest.raises(ValueError, match="SHA-256"):
        verify_local(entry, archive, metadata)


def test_missing_optimizer_is_rejected(tmp_path):
    entry, archive, metadata = make_case(tmp_path, optimizer=False)
    with pytest.raises(ValueError, match="optimizer"):
        verify_local(entry, archive, metadata)


def test_different_engine_is_rejected(tmp_path):
    entry, archive, metadata = make_case(tmp_path, source_hash="wrong")
    with pytest.raises(ValueError, match="engine"):
        verify_local(entry, archive, metadata)


def test_mismatched_steps_are_rejected(tmp_path):
    entry, archive, metadata = make_case(tmp_path, steps=64)
    with pytest.raises(ValueError, match="Step-count"):
        verify_local(entry, archive, metadata)


def test_registry_enforces_unique_ids_and_no_unverified_champion(tmp_path):
    url = "https://github.com/sstxww/reinforcement-learning/releases/download/a/model.zip"
    entry = {"id": "a", "sha256": "a" * 64, "url": url,
             "review_status": "unverified"}
    file = tmp_path / "registry.json"
    data = {"schema": 1, "roles": {"champion": None, "latest": None,
                                   "challenger": None}, "models": [entry]}
    file.write_text(json.dumps(data), encoding="utf-8")
    assert read_registry(file)["models"][0]["id"] == "a"
    data["roles"]["champion"] = "a"
    file.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Champion"):
        read_registry(file)
    data["roles"]["champion"] = None
    data["models"].append(entry.copy())
    file.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        read_registry(file)

def test_schema2_checkpoint_is_supported_and_hash_checked(tmp_path):
    entry, archive, metadata = make_case(tmp_path)
    obj = json.loads(metadata.read_text())
    obj["schema"] = 2
    obj["compatibility"] = {"engine": obj["engine"]}
    obj["checkpoint_sha256"] = entry["sha256"]
    metadata.write_text(json.dumps(obj), encoding="utf-8")
    assert verify_local(entry, archive, metadata)["engine_metadata_verified"]
    obj["checkpoint_sha256"] = "f" * 64
    metadata.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(ValueError, match="metadata SHA-256"):
        verify_local(entry, archive, metadata)


def test_population_and_rejected_references_are_checked(tmp_path):
    entry = {
        "id": "a",
        "sha256": "a" * 64,
        "url": "https://github.com/sstxww/reinforcement-learning/releases/download/a/model.zip",
        "review_status": "unverified",
    }
    data = {"schema": 1, "models": [entry],
            "roles": {"champion": None, "challenger": None, "latest": None,
                      "population": ["not-a-model"], "rejected": []}}
    f = tmp_path / "registry.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Unknown model in population"):
        read_registry(f)
    data["roles"]["population"] = ["a", "a"]
    f.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid population"):
        read_registry(f)
    data["roles"]["population"] = ["a"]
    data["roles"]["rejected"] = ["missing"]
    f.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Unknown model in rejected"):
        read_registry(f)
