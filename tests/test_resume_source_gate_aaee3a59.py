"""Synthetic, non-game tests for fail-closed V5 recovery routing."""
import copy
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tavern_ai.resume_source_gate import release_target, verify_source

ROOT = Path(__file__).resolve().parents[1]


def fixtures(tmp_path):
    source = json.loads((ROOT / "models/registry.json").read_text(encoding="utf-8"))
    index = json.loads((ROOT / "models/release_asset_digests.json").read_text(encoding="utf-8"))
    tag = source["latest"]["id"]
    assert tag == "v5-s-20261102-68099929-1408-41428692617"
    archive = tmp_path / "model.zip"
    with zipfile.ZipFile(archive, "w") as zip_file:
        for name in ("data", "policy.pth", "policy.optimizer.pth"):
            zip_file.writestr(name, b"synthetic unit-test, not trained weights")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    meta = {
        "schema": 1, "algorithm": "MaskablePPO",
        "total_timesteps": source["latest"]["training_steps"],
        "checkpoint_sha256": digest,
        "engine": {
            "version": "1.1.0", "source_hash": "6d8712c93022ba11",
            "features": 4017, "cards": 447, "actions": 245, "n_cards": 3984,
        },
    }
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps(meta), encoding="utf-8")
    for candidate in source["candidates"]:
        if candidate["id"] == tag:
            candidate["checkpoint_sha256"] = digest
    source["latest"]["checkpoint_sha256"] = digest
    for entry in index["assets"]:
        if entry["id"] == tag:
            entry["weights"]["sha256"] = digest
            entry["metadata"]["sha256"] = hashlib.sha256(metadata.read_bytes()).hexdigest()
    registry_path = tmp_path / "registry.json"
    index_path = tmp_path / "index.json"
    registry_path.write_text(json.dumps(source), encoding="utf-8")
    index_path.write_text(json.dumps(index), encoding="utf-8")
    return archive, metadata, registry_path, index_path


def test_latest_is_source_resolved_but_not_champion(tmp_path):
    weights, meta, registry, index = fixtures(tmp_path)
    tag, digest = release_target(registry, index)
    assert tag == "v5-s-20261102-68099929-1408-41428692617"
    assert digest == hashlib.sha256(weights.read_bytes()).hexdigest()
    report = verify_source("release", weights, meta, registry, index)
    assert report["durable_source"] is True
    assert report["champion_promoted"] is False
    assert report["optimizer_continuation_tested"] is False


def test_valid_artifact_requires_checksum(tmp_path):
    weights, meta, registry, index = fixtures(tmp_path)
    result = verify_source("artifact", weights, meta, registry, index)
    assert result["durable_source"] is False
    obj = json.loads(meta.read_text(encoding="utf-8"))
    del obj["checkpoint_sha256"]
    meta.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(ValueError, match="recorded checkpoint digest"):
        verify_source("artifact", weights, meta, registry, index)


def test_corrupt_weights_and_metadata_fail_closed(tmp_path):
    weights, meta, registry, index = fixtures(tmp_path)
    with weights.open("ab") as stream:
        stream.write(b"tampered")
    for origin in ("artifact", "release"):
        with pytest.raises(ValueError, match="SHA256"):
            verify_source(origin, weights, meta, registry, index)
    weights, meta, registry, index = fixtures(tmp_path)
    meta.write_text(meta.read_text(encoding="utf-8").replace('"actions": 245', '"actions": 244'),
                    encoding="utf-8")
    with pytest.raises(ValueError, match="SHA256"):
        verify_source("release", weights, meta, registry, index)
    with pytest.raises(ValueError, match="contract"):
        verify_source("artifact", weights, meta, registry, index)


def test_unregistered_latest_never_auto_falls_back(tmp_path):
    weights, meta, registry, index = fixtures(tmp_path)
    row = json.loads(registry.read_text(encoding="utf-8"))
    row["latest"]["id"] = "untrusted-newer"
    registry.write_text(json.dumps(row), encoding="utf-8")
    with pytest.raises(ValueError):
        release_target(registry, index)


def test_missing_assets_or_unknown_source_fails(tmp_path):
    weights, meta, registry, index = fixtures(tmp_path)
    with pytest.raises(FileNotFoundError):
        verify_source("release", tmp_path / "missing.zip", meta, registry, index)
    with pytest.raises(ValueError, match="Unknown resume origin"):
        verify_source("random", weights, meta, registry, index)
