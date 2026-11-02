"""Fail-closed Release resume tests; no networking or fabricated model weights."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tavern_ai.release_restore_entry import choose_model, restore

ROOT = Path(__file__).resolve().parents[1]


def source():
    registry = json.loads((ROOT / "models/registry.json").read_text(encoding="utf-8"))
    index = json.loads((ROOT / "models/release_asset_digests.json").read_text(encoding="utf-8"))
    return registry, index


def test_latest_is_unpromoted_and_matches_canonical_registry():
    registry, index = source()
    selected = choose_model(registry, index)
    assert selected["id"] == registry["latest"]["id"]
    assert selected["role"] == "candidate_unpromoted"
    assert registry["champion"] is None and registry["best"] is None


def test_no_unindexed_or_unproven_checkpoint():
    registry, index = source()
    with pytest.raises(ValueError, match="Not an indexed"):
        choose_model(registry, index, "not-a-real-release")
    tampered = copy.deepcopy(registry)
    tampered["latest"]["id"] = "not-a-real-release"
    with pytest.raises(ValueError):
        choose_model(tampered, index)


def test_asset_catalog_mismatch_blocks_download():
    registry, index = source()
    tampered = copy.deepcopy(index)
    latest = registry["latest"]["id"]
    record = next(a for a in tampered["assets"] if a["id"] == latest)
    record["weights"]["sha256"] = "f" * 64
    with pytest.raises(ValueError, match="mismatch"):
        choose_model(registry, tampered)


def test_missing_token_rejects_before_checkpoint_creation(tmp_path, monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="GH_TOKEN"):
        restore(ROOT / "models/registry.json",
                ROOT / "models/release_asset_digests.json",
                tmp_path / "checkpoint", check_load=False)
    assert not (tmp_path / "checkpoint" / "model.zip").exists()


def test_existing_checkpoint_never_overwritten(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "dummy-not-used")
    output = tmp_path / "checkpoints"
    output.mkdir()
    (output / "model.zip").write_bytes(b"unique-old-checkpoint")
    with pytest.raises(FileExistsError, match="overwrite"):
        restore(ROOT / "models/registry.json",
                ROOT / "models/release_asset_digests.json",
                output, check_load=False)
    assert (output / "model.zip").read_bytes() == b"unique-old-checkpoint"
