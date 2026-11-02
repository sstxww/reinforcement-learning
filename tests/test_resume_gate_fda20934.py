"""Offline regression gates for main's scheduled PPO continuity."""
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES
from tavern_ai.resume_gate_fda20934 import decide_resume


def _pair(tmp_path, *, digest=True):
    checkpoint = tmp_path / "model.zip"
    metadata = tmp_path / "model.metadata.json"
    with zipfile.ZipFile(checkpoint, "w") as z:
        for name in ("data", "policy.pth", "policy.optimizer.pth"):
            z.writestr(name, b"test")
    doc = {
        "schema": 1,
        "algorithm": "MaskablePPO",
        "total_timesteps": 1280,
        "engine": {"version": "1.1.0", "source_hash": ENGINE_HASH,
                   "features": FEATURES, "cards": CARDS, "actions": ACTIONS},
    }
    if digest:
        doc["checkpoint_sha256"] = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    metadata.write_text(json.dumps(doc), encoding="utf-8")
    return checkpoint, metadata


def test_missing_checkpoint_cannot_silently_restart(tmp_path):
    p, m = tmp_path / "model.zip", tmp_path / "model.metadata.json"
    with pytest.raises(ValueError, match="silent random"):
        decide_resume(p, m)
    assert decide_resume(p, m, allow_fresh=True)["mode"] == "fresh"


def test_incomplete_pair_never_restarts_even_when_explicit(tmp_path):
    p, m = tmp_path / "model.zip", tmp_path / "model.metadata.json"
    p.write_bytes(b"incomplete")
    with pytest.raises(ValueError, match="Incomplete"):
        decide_resume(p, m, allow_fresh=True)


def test_valid_pair_preserves_cumulative_steps(tmp_path):
    p, m = _pair(tmp_path)
    result = decide_resume(p, m)
    assert result["mode"] == "resume"
    assert result["total_timesteps"] == 1280
    assert result["local_metadata_digest_matched"] is True
    assert result["external_release_provenance_verified"] is False


def test_legacy_pair_does_not_claim_checksum_provenance(tmp_path):
    p, m = _pair(tmp_path, digest=False)
    assert decide_resume(p, m)["local_metadata_digest_matched"] is False


def test_bad_hash_blocks_resume_and_fresh(tmp_path):
    p, m = _pair(tmp_path)
    p.write_bytes(p.read_bytes() + b"tamper")
    with pytest.raises(ValueError, match="differ"):
        decide_resume(p, m, allow_fresh=True)


def test_mismatched_action_contract_blocks_resume(tmp_path):
    p, m = _pair(tmp_path)
    doc = json.loads(m.read_text())
    doc["engine"]["actions"] -= 1
    m.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="contract"):
        decide_resume(p, m)


def test_corrupted_zip_blocks_resume(tmp_path):
    p, m = _pair(tmp_path, digest=False)
    p.write_bytes(b"not-a-zip")
    with pytest.raises(ValueError, match="Corrupt"):
        decide_resume(p, m)


def test_negative_steps_are_not_valid_checkpoint(tmp_path):
    p, m = _pair(tmp_path, digest=False)
    doc = json.loads(m.read_text())
    doc["total_timesteps"] = 0
    m.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="cumulative"):
        decide_resume(p, m)
