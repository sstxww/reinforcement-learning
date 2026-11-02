"""P1 regression gates: do not train on untrusted or wrongly identified weights."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tavern_ai.verified_resume_70d8074c import (
    sha256, validate_budget, verified_source, resume_once,
)

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "v5-s-20261102-68099929-1408-41428692617"


@pytest.mark.parametrize("steps", [-1, 0, 1, 127, 129, 513, 10000, 128.0, True])
def test_budget_rejects_invalid_and_large_training(steps):
    with pytest.raises(ValueError):
        validate_budget(steps)


@pytest.mark.parametrize("steps", [128, 256, 384, 512])
def test_explicit_small_resume_budget_allowed(steps):
    validate_budget(steps)


def test_canonical_registry_has_no_promoted_champion():
    registry = json.loads((ROOT / "models/registry.json").read_text())
    assert registry["best"] is None and registry["champion"] is None
    assert any(c["id"] == MODEL_ID and c["training_steps"] == 1408 for c in registry["candidates"])


def test_digest_is_actual_file_content(tmp_path):
    file = tmp_path / "model.zip"
    file.write_bytes(b"original")
    assert sha256(file) == hashlib.sha256(b"original").hexdigest()
    file.write_bytes(b"tampered")
    assert sha256(file) != hashlib.sha256(b"original").hexdigest()


def test_unknown_release_id_fails_closed(tmp_path):
    weights = tmp_path / "model.zip"
    meta = tmp_path / "model.metadata.json"
    weights.write_bytes(b"fake weights")
    meta.write_text('{"schema":1}')
    with pytest.raises(ValueError, match="Unknown or promoted"):
        verified_source("unknown-id", weights, meta)


def test_registered_but_tampered_bytes_fail_before_deserialization(tmp_path):
    weights = tmp_path / "model.zip"
    meta = tmp_path / "model.metadata.json"
    weights.write_bytes(b"not a trained checkpoint")
    meta.write_text('{"schema":1}')
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        verified_source(MODEL_ID, weights, meta, probe=False)


def test_model_resume_refuses_missing_metadata_before_training(tmp_path):
    weights = tmp_path / "model.zip"
    weights.write_bytes(b"dummy")
    with pytest.raises(FileNotFoundError):
        resume_once(MODEL_ID, weights, tmp_path / "model.metadata.json", 128,
                    73021, tmp_path / "out.zip", tmp_path / "summary.json")


def test_model_resume_refuses_wrong_metadata_location(tmp_path):
    weights = tmp_path / "model.zip"
    meta = tmp_path / "different.metadata.json"
    weights.write_bytes(b"dummy")
    meta.write_text("{}")
    with pytest.raises(ValueError, match="adjacent"):
        resume_once(MODEL_ID, weights, meta, 128, 73021,
                    tmp_path / "out.zip", tmp_path / "summary.json")


def test_model_resume_refuses_overwriting_checkpoint(tmp_path):
    weights = tmp_path / "model.zip"
    meta = tmp_path / "model.metadata.json"
    weights.write_bytes(b"dummy")
    meta.write_text("{}")
    with pytest.raises(ValueError, match="separate"):
        resume_once(MODEL_ID, weights, meta, 128, 73021,
                    weights, tmp_path / "summary.json")


def test_model_resume_refuses_overwriting_existing_report(tmp_path):
    weights = tmp_path / "model.zip"
    meta = tmp_path / "model.metadata.json"
    weights.write_bytes(b"dummy")
    meta.write_text("{}")
    out_report = tmp_path / "summary.json"
    out_report.write_text("{}")
    with pytest.raises(ValueError, match="refusing overwrite"):
        resume_once(MODEL_ID, weights, meta, 128, 73021,
                    tmp_path / "out.zip", out_report)
