"""Offline registry tests; synthetic ZIP fixtures are never game/model receipts."""
import copy
import hashlib
import io
import json
import zipfile
from pathlib import Path
import pytest
from tavern_ai.checkpoint_catalog import CatalogError, ENGINE, validate_catalog, verify_files

def catalog():
    return json.loads(Path("models/registry.json").read_text(encoding="utf-8"))

def test_release_index_has_no_unsupported_champion():
    data = catalog()
    indexed = validate_catalog(data)
    assert len(indexed) == 2
    assert data["champion"] is None and data["latest"] is None
    assert not any(x["download_verified"] for x in indexed.values())

def test_duplicates_and_bad_contract_are_rejected():
    data = catalog()
    data["models"].append(copy.deepcopy(data["models"][0]))
    with pytest.raises(CatalogError, match="Duplicate"):
        validate_catalog(data)
    data = catalog()
    data["models"][0]["engine"]["actions"] = 111
    with pytest.raises(CatalogError, match="engine"):
        validate_catalog(data)

@pytest.mark.parametrize("pointer", ["latest", "champion"])
def test_unverified_candidates_cannot_be_promoted(pointer):
    data = catalog()
    data[pointer] = data["models"][0]["id"]
    with pytest.raises(CatalogError):
        validate_catalog(data)

def test_bad_parent_fails():
    data = catalog()
    data["models"][1]["parent"] = "missing"
    with pytest.raises(CatalogError, match="parent"):
        validate_catalog(data)

def test_offline_hash_crc_and_metadata(tmp_path):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("synthetic.txt", "fixture only, not a PPO model")
    w = tmp_path / "weights.zip"
    w.write_bytes(output.getvalue())
    m = tmp_path / "model.metadata.json"
    m.write_text(json.dumps({"algorithm": "MaskablePPO", "engine": ENGINE,
                             "total_timesteps": 256}), encoding="utf-8")
    entry = copy.deepcopy(catalog()["models"][0])
    entry["assets"]["weights"]["sha256"] = hashlib.sha256(w.read_bytes()).hexdigest()
    entry["assets"]["metadata"]["sha256"] = hashlib.sha256(m.read_bytes()).hexdigest()
    result = verify_files(entry, w, m)
    assert result["metadata_verified"] and not result["model_load_tested"]
    m.write_text(m.read_text().replace("245", "246"), encoding="utf-8")
    with pytest.raises(CatalogError, match="SHA256"):
        verify_files(entry, w, m)

def test_corrupt_zip_rejected_even_with_matching_sha(tmp_path):
    w = tmp_path / "bad.zip"
    w.write_bytes(b"not actually model weights")
    m = tmp_path / "model.metadata.json"
    m.write_text(json.dumps({"algorithm": "MaskablePPO", "engine": ENGINE,
                             "total_timesteps": 256}), encoding="utf-8")
    entry = copy.deepcopy(catalog()["models"][0])
    entry["assets"]["weights"]["sha256"] = hashlib.sha256(w.read_bytes()).hexdigest()
    entry["assets"]["metadata"]["sha256"] = hashlib.sha256(m.read_bytes()).hexdigest()
    with pytest.raises(CatalogError, match="ZIP"):
        verify_files(entry, w, m)
