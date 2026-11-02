"""Synthetic pre-learn safety regression; never a real PPO/game receipt."""
from __future__ import annotations

import hashlib
import json
import sys
import types

import pytest

from tavern_ai import train
from tavern_ai.contract import (
    ENGINE_HASH, FEATURES, CARDS, ACTIONS,
    CATALOG_SHA256, PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT,
)

ENGINE = {
    "version": "1.1.0", "source_hash": ENGINE_HASH,
    "features": FEATURES, "cards": CARDS, "actions": ACTIONS, "n_cards": 4096,
}
COMPAT = {
    "engine": ENGINE, "catalog_sha256": CATALOG_SHA256,
    "patch_sha256": PATCH_SHA256, "ruleset_id": RULESET_ID,
    "upstream_commit": UPSTREAM_COMMIT,
}


def test_correct_schema2_and_legacy_schema1_pass_preflight():
    train.verify_parent_before_load(ENGINE, {
        "schema": 1, "engine": ENGINE, "total_timesteps": 256,
    })
    train.verify_parent_before_load(ENGINE, {
        "schema": 2, "engine": ENGINE, "total_timesteps": 1280,
        "compatibility": COMPAT,
    })


@pytest.mark.parametrize("parent", [
    {"schema": 2, "engine": ENGINE, "total_timesteps": 1280},
    {"schema": 2, "engine": ENGINE, "total_timesteps": 1280,
     "compatibility": {**COMPAT, "patch_sha256": "wrong"}},
    {"schema": 3, "engine": ENGINE, "total_timesteps": 1280},
    {"schema": True, "engine": ENGINE, "total_timesteps": 1280},
    {"schema": 1, "engine": ENGINE, "total_timesteps": 0},
    {"schema": 2, "engine": {**ENGINE, "actions": 244},
     "total_timesteps": 1280, "compatibility": COMPAT},
])
def test_invalid_parent_fails_closed_before_model_load(parent):
    with pytest.raises(ValueError):
        train.verify_parent_before_load(ENGINE, parent)


def test_run_rejects_incompatible_schema2_before_model_deserialization(monkeypatch, tmp_path):
    archive = tmp_path / "source.zip"
    archive.write_bytes(b"synthetic parent archive; no PPO weights")
    metadata = {
        "schema": 2, "engine": ENGINE, "total_timesteps": 1280,
        "compatibility": {**COMPAT, "patch_sha256": "tampered"},
        "checkpoint_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }
    archive.with_suffix(".metadata.json").write_text(json.dumps(metadata))
    observed = {"load": 0, "env_closed": 0}

    class PoisonModel:
        @staticmethod
        def load(*args, **kwargs):
            observed["load"] += 1
            raise AssertionError("PPO load must not run for incompatible schema2")

    class FakeEnv:
        def __init__(self, *args, **kwargs):
            pass

        def close(self):
            observed["env_closed"] += 1

    monkeypatch.setattr(train, "verify_engine", lambda: ENGINE)
    monkeypatch.setattr(train, "TavernEnv", FakeEnv)
    monkeypatch.setitem(sys.modules, "sb3_contrib", types.SimpleNamespace(MaskablePPO=PoisonModel))
    monkeypatch.setitem(sys.modules, "tavern_ai.model", types.SimpleNamespace(TavernExtractor=object))
    with pytest.raises(ValueError, match="compatibility provenance mismatch before PPO load"):
        train.run(steps=128, seed=42, model_out=tmp_path / "new.zip", resume=archive)
    assert observed == {"load": 0, "env_closed": 1}
