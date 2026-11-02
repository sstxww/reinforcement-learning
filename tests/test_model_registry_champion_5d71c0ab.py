"""Synthetic-only Champion approval tests. No game or trained-weight claims."""
import json
from pathlib import Path

import pytest

from tavern_ai.model_registry import read_registry

SESSION = "s-20261102-5d71c0ab"
FLAGS = (
    "durable_download_verified", "hash_verified", "load_verified",
    "resume_verified", "complete_match_verified", "competitive_gain_verified",
)


def sample():
    tag = "synthetic-test-release"
    return {
        "schema": 1,
        "models": [{
            "id": tag, "review_status": "verified", "sha256": "a" * 64,
            "url": f"https://github.com/sstxww/reinforcement-learning/releases/download/{tag}/model.zip",
        }],
        "roles": {"champion": tag, "challenger": None, "latest": None,
                  "population": [], "rejected": []},
    }


def validate(tmp_path: Path, registry: dict):
    dest = tmp_path / "registry.json"
    dest.write_text(json.dumps(registry), encoding="utf-8")
    return read_registry(dest)


def test_verified_label_alone_cannot_promote(tmp_path):
    with pytest.raises(ValueError, match="Champion requires positive independent evidence"):
        validate(tmp_path, sample())


@pytest.mark.parametrize("missing", FLAGS)
def test_each_champion_evidence_flag_is_mandatory(tmp_path, missing):
    obj = sample()
    obj["models"][0].update({flag: True for flag in FLAGS})
    obj["models"][0][missing] = False
    with pytest.raises(ValueError, match=missing):
        validate(tmp_path, obj)
    obj["models"][0][missing] = "true"  # strings are not evidence
    with pytest.raises(ValueError, match=missing):
        validate(tmp_path, obj)


def test_complete_evidence_eligibility_only_not_strength_proof(tmp_path):
    obj = sample()
    obj["models"][0].update({flag: True for flag in FLAGS})
    assert validate(tmp_path, obj)["roles"]["champion"] == obj["models"][0]["id"]


@pytest.mark.parametrize("group", ["population", "rejected"])
def test_roles_cannot_refer_to_missing_or_duplicate_models(tmp_path, group):
    obj = sample()
    obj["roles"]["champion"] = None
    obj["roles"][group] = ["missing"]
    with pytest.raises(ValueError, match="Invalid"):
        validate(tmp_path, obj)
    obj["roles"][group] = [obj["models"][0]["id"]] * 2
    with pytest.raises(ValueError, match="Invalid"):
        validate(tmp_path, obj)


def test_canonical_release_catalog_remains_unpromoted():
    path = Path(__file__).resolve().parents[1] / "models" / "release_inventory_v5.json"
    obj = read_registry(path)
    assert obj["roles"]["champion"] is None
