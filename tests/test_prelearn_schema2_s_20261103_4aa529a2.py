"""Regression: incompatible resumed schema-2 parents must fail before PPO load/learn."""
import json
import sys
import types

import pytest

from tavern_ai.contract import (
    ACTIONS, CARDS, ENGINE_HASH, FEATURES, CATALOG_SHA256,
    PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT,
)
from tavern_ai.train import validate_resume_parent
from tavern_ai import train

ENGINE = {
    "version": "1.1.0", "source_hash": ENGINE_HASH,
    "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
    "n_cards": 4096,
}
COMPAT = {
    "engine": ENGINE, "catalog_sha256": CATALOG_SHA256,
    "patch_sha256": PATCH_SHA256, "ruleset_id": RULESET_ID,
    "upstream_commit": UPSTREAM_COMMIT,
}
PARENT = {
    "schema": 2, "engine": ENGINE, "total_timesteps": 1280,
    "increment_timesteps": 1024, "compatibility": COMPAT,
}


def test_valid_schema1_and_schema2_parent_are_accepted():
    validate_resume_parent(PARENT, ENGINE)
    validate_resume_parent({"schema": 1, "engine": ENGINE, "total_timesteps": 256}, ENGINE)


@pytest.mark.parametrize("change", [
    {"schema": 3},
    {"schema": True},
    {"schema": 2.0},
    {"compatibility": {**COMPAT, "catalog_sha256": "tampered"}},
    {"compatibility": None},
    {"increment_timesteps": 0},
    {"increment_timesteps": 1281},
    {"increment_timesteps": True},
    {"total_timesteps": "1280"},
    {"engine": {**ENGINE, "actions": 244}},
])
def test_incompatible_parent_is_rejected(change):
    with pytest.raises(ValueError):
        validate_resume_parent({**PARENT, **change}, ENGINE)


def test_invalid_schema2_cannot_load_or_train(tmp_path, monkeypatch):
    resume = tmp_path / "parent.zip"
    resume.write_bytes(b"synthetic placeholder, never deserialized")
    bad = {**PARENT, "compatibility": {**COMPAT, "ruleset_id": "tampered"}}
    resume.with_suffix(".metadata.json").write_text(json.dumps(bad), encoding="utf-8")
    class Env:
        closed = False
        def close(self):
            self.closed = True
    env = Env()
    monkeypatch.setattr(train, "verify_engine", lambda: ENGINE)
    monkeypatch.setattr(train, "TavernEnv", lambda seed: env)
    monkeypatch.setattr(train, "require_verified_resume", lambda *args: "a" * 64)
    class NoPPO:
        @staticmethod
        def load(*args, **kwargs):
            pytest.fail("MaskablePPO.load must never run for incompatible metadata")
    fake_sb3 = types.ModuleType("sb3_contrib")
    fake_sb3.MaskablePPO = NoPPO
    monkeypatch.setitem(sys.modules, "sb3_contrib", fake_sb3)
    fake_model = types.ModuleType("tavern_ai.model")
    fake_model.TavernExtractor = object
    monkeypatch.setitem(sys.modules, "tavern_ai.model", fake_model)
    with pytest.raises(ValueError, match="compatibility provenance mismatch"):
        train.run(steps=128, seed=42, model_out=tmp_path / "candidate.zip", resume=resume)
    assert env.closed
    assert not (tmp_path / "candidate.zip").exists()
