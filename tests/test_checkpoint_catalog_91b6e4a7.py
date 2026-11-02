"""Independent offline regression: main registry + two Release file digests."""
import copy
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pytest

from tavern_ai.checkpoint_catalog import (CatalogError, ENGINE, METADATA_SHA256,
                                          validate_catalog, verify_files)

ROOT = Path(__file__).resolve().parents[1]

def registry():
    return json.loads((ROOT / "models" / "registry.json").read_text(encoding="utf-8"))

def test_only_canonical_main_registry_and_no_champion():
    data = registry()
    records = validate_catalog(data)
    # A published, unpromoted Release may be appended to the canonical registry
    # before this historical verifier has a pinned metadata digest for it.
    # Pinned entries are a deliberately audited subset, not a frozen census.
    assert len(records) == len(data["candidates"])
    assert set(METADATA_SHA256).issubset(set(records))
    assert data["latest"]["id"] in records
    assert data["best"] is None and data["champion"] is None
    assert data["latest"]["role"] == "latest_experimental_unpromoted"

def test_duplicate_model_ids_and_incompatible_engine_fail_closed():
    data = registry()
    data["candidates"].append(copy.deepcopy(data["candidates"][0]))
    with pytest.raises(CatalogError, match="duplicate"):
        validate_catalog(data)
    data = registry()
    data["engine"]["action_count"] = 999
    with pytest.raises(CatalogError, match="contract"):
        validate_catalog(data)

@pytest.mark.parametrize("pointer", ["champion", "best"])
def test_unverified_promotion_not_allowed(pointer):
    data = registry()
    data[pointer] = data["candidates"][0]["id"]
    with pytest.raises(CatalogError):
        validate_catalog(data)

def test_wrong_latest_provenance_rejected():
    data = registry()
    data["latest"]["checkpoint_sha256"] = "f" * 64
    with pytest.raises(CatalogError, match="provenance"):
        validate_catalog(data)

def test_both_asset_hashes_zip_crc_and_metadata(tmp_path):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("fixture", "Not a trained model; synthetic ZIP")
    weights = tmp_path / "model.zip"
    weights.write_bytes(output.getvalue())
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps({"algorithm": "MaskablePPO", "engine": ENGINE,
                                   "total_timesteps": 256}), encoding="utf-8")
    entry = copy.deepcopy(registry()["candidates"][0])
    assert entry["training_steps"] == 256
    entry["checkpoint_sha256"] = hashlib.sha256(weights.read_bytes()).hexdigest()
    meta_sha = hashlib.sha256(metadata.read_bytes()).hexdigest()
    report = verify_files(entry, weights, metadata, meta_sha)
    assert report["sha256_verified"] and report["metadata_contract_verified"]
    assert report["model_deserialized"] is False
    assert report["optimizer_resume_tested"] is False
    metadata.write_text(metadata.read_text().replace("245", "246"), encoding="utf-8")
    with pytest.raises(CatalogError, match="Metadata SHA256"):
        verify_files(entry, weights, metadata, meta_sha)

def test_corrupt_zip_fails_even_with_matching_digest(tmp_path):
    weights = tmp_path / "model.zip"
    weights.write_bytes(b"not a ZIP and never a real checkpoint")
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps({"algorithm": "MaskablePPO", "engine": ENGINE,
                                   "total_timesteps": 256}), encoding="utf-8")
    entry = copy.deepcopy(registry()["candidates"][0])
    entry["checkpoint_sha256"] = hashlib.sha256(weights.read_bytes()).hexdigest()
    meta_sha = hashlib.sha256(metadata.read_bytes()).hexdigest()
    with pytest.raises(CatalogError, match="ZIP"):
        verify_files(entry, weights, metadata, meta_sha)

def test_wrong_algorithm_or_steps_rejected_after_asset_hashes(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr("fixture", "not a policy")
    weights = tmp_path / "model.zip"
    weights.write_bytes(buf.getvalue())
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({"algorithm": "Q-learning", "engine": ENGINE,
                                   "total_timesteps": 255}), encoding="utf-8")
    entry = copy.deepcopy(registry()["candidates"][0])
    entry["checkpoint_sha256"] = hashlib.sha256(weights.read_bytes()).hexdigest()
    meta_sha = hashlib.sha256(metadata.read_bytes()).hexdigest()
    with pytest.raises(CatalogError, match="algorithm"):
        verify_files(entry, weights, metadata, meta_sha)
