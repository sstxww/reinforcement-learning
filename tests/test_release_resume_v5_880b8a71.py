"""Synthetic unit fixtures only; never count these files as real game evidence."""
import hashlib
import json
import zipfile

import pytest

from scripts.verify_release_resume_v5_880b8a71 import check_source, attest_resumed


def fixture(tmp_path):
    original = tmp_path / "source.zip"
    with zipfile.ZipFile(original, "w") as archive:
        archive.writestr("policy.pth", b"fake-source" * 16)
    sha = hashlib.sha256(original.read_bytes()).hexdigest()
    engine = {"version": "1.1.0", "source_hash": "6d8712c93022ba11"}
    provenance = {"engine": engine, "catalog_sha256": "x",
                  "ruleset_id": "x", "patch_sha256": "x", "upstream_commit": "x"}
    meta = tmp_path / "source.metadata.json"
    meta.write_text(json.dumps({"schema": 2, "checkpoint_sha256": sha, "total_timesteps": 1280,
                                "algorithm": "MaskablePPO", "engine": engine,
                                "compatibility": provenance}))
    return original, meta, sha


def test_valid_source(tmp_path):
    model, meta, sha = fixture(tmp_path)
    assert check_source(model, meta, expected_hash=sha)["total_timesteps"] == 1280


@pytest.mark.parametrize("tamper", ["hash", "steps", "engine", "catalog"])
def test_fail_closed_before_model_load(tmp_path, tamper):
    model, meta, sha = fixture(tmp_path)
    d = json.loads(meta.read_text())
    if tamper == "hash":
        model.write_bytes(model.read_bytes() + b"tamper")
    if tamper == "steps":
        d["total_timesteps"] = 256
    if tamper == "engine":
        d["engine"]["source_hash"] = "wrong"
    if tamper == "catalog":
        d["compatibility"]["catalog_sha256"] = ""
    meta.write_text(json.dumps(d))
    with pytest.raises(ValueError):
        check_source(model, meta, expected_hash=sha)


def test_actual_continuation_must_increment_and_persist_hash(tmp_path):
    original, original_meta, sha = fixture(tmp_path)
    target = tmp_path / "resumed.zip"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("policy.pth", b"changed-weights" * 16)
    new_meta = tmp_path / "resumed.metadata.json"
    parent = json.loads(original_meta.read_text())
    new_meta.write_text(json.dumps({"engine": parent["engine"], "algorithm": "MaskablePPO",
                                    "total_timesteps": 1408}))
    report = tmp_path / "report.json"
    result = attest_resumed(original, original_meta, target, new_meta, report,
                            expected_hash=sha)
    assert result["resumed_total_timesteps"] == 1408
    assert result["promotion"] == "none"
    saved = json.loads(new_meta.read_text())
    assert saved["compatibility"] == parent["compatibility"]
    assert saved["checkpoint_sha256"] == hashlib.sha256(target.read_bytes()).hexdigest()


def test_reject_nonincremented_steps(tmp_path):
    original, original_meta, sha = fixture(tmp_path)
    target = tmp_path / "resumed.zip"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("policy.pth", b"something" * 20)
    new_meta = tmp_path / "resumed.metadata.json"
    new_meta.write_text(json.dumps({"engine": json.loads(original_meta.read_text())["engine"],
                                    "algorithm": "MaskablePPO", "total_timesteps": 1280}))
    with pytest.raises(ValueError, match="exactly"):
        attest_resumed(original, original_meta, target, new_meta, tmp_path / "r.json",
                       expected_hash=sha)
