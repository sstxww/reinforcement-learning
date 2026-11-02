"""Offline tests for the isolated Release-backed 128-step resume smoke.

No synthetic test is represented as a real trained model or game.
"""
from pathlib import Path
import json
import pytest

from tavern_ai.resume_smoke_fb6a2c91 import (
    SOURCE_ID, SESSION, lineage_record, smoke,
)

ROOT = Path(__file__).resolve().parents[1]
PARENT_HASH = "a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632"


def test_canonical_parent_is_unpromoted_and_has_two_hash_pinned_release_assets():
    registry = json.loads((ROOT / "models/registry.json").read_text(encoding="utf-8"))
    assets = json.loads((ROOT / "models/release_asset_digests.json").read_text(encoding="utf-8"))
    parent = next(m for m in registry["candidates"] if m["id"] == SOURCE_ID)
    indexed = next(a for a in assets["assets"] if a["id"] == SOURCE_ID)
    assert parent["training_steps"] == 1408
    assert parent["checkpoint_sha256"] == PARENT_HASH == indexed["weights"]["sha256"]
    assert len(indexed["metadata"]["sha256"]) == 64
    assert registry["best"] is None and registry["champion"] is None


def test_valid_resume_lineage_requires_incremental_steps_and_changed_weights():
    child_hash = "a" * 64
    out = lineage_record(SOURCE_ID, 1408, PARENT_HASH, 1536, child_hash, 128)
    assert out["parent_steps"] == 1408
    assert out["added_steps"] == 128
    assert out["child_steps"] == 1536
    assert out["child_sha256"] == child_hash
    assert out["session_id"] == SESSION
    assert out["state"] == "unpromoted_checkpoint"
    assert out["competitive_improvement"] == "not_established"


@pytest.mark.parametrize("steps,added", [(1408, 128), (1540, 128), (1536, 0), (1536, -1)])
def test_bad_resume_step_counters_rejected(steps, added):
    with pytest.raises(ValueError):
        lineage_record(SOURCE_ID, 1408, PARENT_HASH, steps, "a" * 64, added)


def test_missing_hash_and_unchanged_checkpoint_rejected():
    with pytest.raises(ValueError, match="SHA256"):
        lineage_record(SOURCE_ID, 1408, "bad", 1536, "a" * 64, 128)
    with pytest.raises(ValueError, match="unchanged"):
        lineage_record(SOURCE_ID, 1408, PARENT_HASH, 1536, PARENT_HASH, 128)


def test_smoke_refuses_any_large_budget_before_io(tmp_path):
    with pytest.raises(ValueError, match="128-step"):
        smoke(tmp_path / "old.zip", tmp_path / "new.zip",
              tmp_path / "record.json", 2048, 1,
              ROOT / "models/registry.json", ROOT / "models/release_asset_digests.json")


def test_smoke_never_overwrites_parent_or_fakes_missing_release(tmp_path):
    source = tmp_path / "source.zip"
    with pytest.raises(ValueError, match="overwrite"):
        smoke(source, source, tmp_path / "record.json", 128, 1,
              ROOT / "models/registry.json", ROOT / "models/release_asset_digests.json")
    with pytest.raises(FileNotFoundError):
        smoke(source, tmp_path / "candidate.zip", tmp_path / "record.json", 128, 1,
              ROOT / "models/registry.json", ROOT / "models/release_asset_digests.json")
