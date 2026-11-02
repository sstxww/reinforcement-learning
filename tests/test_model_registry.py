"""Existing main registry + independently checkable release archive preflight tests."""
from __future__ import annotations
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tavern_ai.contract import (
    ACTIONS, CARDS, ENGINE_HASH, FEATURES,
    CATALOG_SHA256, RULESET_ID, PATCH_SHA256, UPSTREAM_COMMIT,
)
from tavern_ai.model_registry import read_registry, verify_archive


def fixture(tmp_path, schema=1):
    checkpoint = tmp_path / "model.zip"
    with zipfile.ZipFile(checkpoint, "w") as archive:
        for name in ("data", "policy.pth", "policy.optimizer.pth"):
            archive.writestr(name, b"offline-test-only")
    sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    entry = {
        "id": "test-checkpoint", "checkpoint_sha256": sha, "training_steps": 128,
        "role": "candidate_unpromoted",
        "release_url": "https://github.com/sstxww/reinforcement-learning/releases/tag/test-checkpoint",
    }
    metadata = tmp_path / "model.metadata.json"
    engine = {
        "version": "1.1.0", "source_hash": ENGINE_HASH,
        "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
    }
    payload = {"schema": schema, "algorithm": "MaskablePPO",
               "total_timesteps": 128, "engine": engine}
    if schema == 2:
        payload["checkpoint_sha256"] = sha
        payload["compatibility"] = {
            "engine": engine, "catalog_sha256": CATALOG_SHA256,
            "ruleset_id": RULESET_ID, "patch_sha256": PATCH_SHA256,
            "upstream_commit": UPSTREAM_COMMIT,
        }
    metadata.write_text(json.dumps(payload), encoding="utf-8")
    return checkpoint, metadata, entry


def test_reads_real_canonical_four_model_registry():
    r = read_registry(Path("models/registry.json"))
    assert r["champion"] is None and r["best"] is None
    assert len(r["candidates"]) >= 4
    assert r["latest"]["id"] == "v2-learning-41413557445"


@pytest.mark.parametrize("schema", [1, 2])
def test_accepts_expected_structure_without_claiming_restore(tmp_path, schema):
    checkpoint, metadata, entry = fixture(tmp_path, schema)
    result = verify_archive(entry, checkpoint, metadata)
    assert result["optimizer_member_present"]
    assert not result["load_or_resume_verified_by_this_preflight"]


def test_rejects_sha_mismatch(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path)
    entry["checkpoint_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="SHA256"):
        verify_archive(entry, checkpoint, metadata)


def test_rejects_incompatible_card_schema(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path)
    payload = json.loads(metadata.read_text())
    payload["engine"]["cards"] = CARDS - 1
    metadata.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="Engine"):
        verify_archive(entry, checkpoint, metadata)


def test_rejects_missing_optimizer(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path)
    with zipfile.ZipFile(checkpoint, "w") as archive:
        archive.writestr("data", b"offline-test-only")
        archive.writestr("policy.pth", b"offline-test-only")
    entry["checkpoint_sha256"] = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="optimizer"):
        verify_archive(entry, checkpoint, metadata)


def test_rejects_champion_in_existing_registry(tmp_path):
    data = read_registry(Path("models/registry.json"))
    data["champion"] = data["latest"]["id"]
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Champion"):
        read_registry(path)


def test_rejects_duplicate_existing_registry_ids(tmp_path):
    data = read_registry(Path("models/registry.json"))
    data["candidates"].append(dict(data["candidates"][0]))
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Duplicate"):
        read_registry(path)


def test_schema2_catalog_fingerprint_must_match(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path, 2)
    payload = json.loads(metadata.read_text())
    payload["compatibility"]["catalog_sha256"] = "incorrect"
    metadata.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="catalog"):
        verify_archive(entry, checkpoint, metadata)


def test_schema2_embedded_checkpoint_hash_must_match(tmp_path):
    checkpoint, metadata, entry = fixture(tmp_path, 2)
    payload = json.loads(metadata.read_text())
    payload["checkpoint_sha256"] = "0" * 64
    metadata.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="Embedded"):
        verify_archive(entry, checkpoint, metadata)
