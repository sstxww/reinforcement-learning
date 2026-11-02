"""Synthetic provenance regression only; not a real model/game attestation."""
import json
import pytest
from tavern_ai.model_registry import read_registry

REQUIRED = (
    "durable_download_verified", "hash_verified", "load_verified",
    "resume_verified", "complete_match_verified",
    "unassisted_complete_match_verified",
    "independent_paired_evaluation_verified", "competitive_gain_verified",
)


def registry(tmp_path, **evidence):
    entry = {
        "id": "synthetic-test-model",
        "sha256": "a" * 64,
        "url": "https://github.com/sstxww/reinforcement-learning/releases/download/synthetic-test-model/model.zip",
        "review_status": "verified",
        **evidence,
    }
    doc = {"schema": 1, "models": [entry],
           "roles": {"champion": entry["id"], "challenger": None, "latest": None}}
    p = tmp_path / "registry.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


def test_review_status_alone_never_promotes(tmp_path):
    with pytest.raises(ValueError, match="Champion evidence incomplete"):
        read_registry(registry(tmp_path))


@pytest.mark.parametrize("missing", REQUIRED)
def test_each_champion_provenance_gate_is_mandatory(tmp_path, missing):
    values = {k: True for k in REQUIRED}
    values[missing] = False
    values["safety_fallback_used"] = False
    with pytest.raises(ValueError, match=missing):
        read_registry(registry(tmp_path, **values))


def test_assisted_game_cannot_be_certified_as_raw_champion(tmp_path):
    values = {k: True for k in REQUIRED}
    values["safety_fallback_used"] = True
    with pytest.raises(ValueError, match="safety fallback"):
        read_registry(registry(tmp_path, **values))


def test_all_flags_are_only_structurally_accepted_not_evidence_of_strength(tmp_path):
    values = {k: True for k in REQUIRED}
    values["safety_fallback_used"] = False
    doc = read_registry(registry(tmp_path, **values))
    assert doc["roles"]["champion"] == "synthetic-test-model"


def test_current_release_inventory_never_promotes(tmp_path):
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "models" / "release_inventory_v5.json"
    doc = read_registry(p)
    assert doc["roles"]["champion"] is None
