"""Lightweight training-contract tests with no TavernGym or PPO dependency."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

ENGINE = {"source_hash": "pin", "version": "1.1.0"}


def test_refuse_corrupt_resume_before_deserialization(monkeypatch, tmp_path):
    state = {"load_calls": 0, "closed": 0}
    envmod = ModuleType("tavern_ai.env")
    class StubEnv:
        def __init__(self, seed): self.seed = seed
        def close(self): state["closed"] += 1
    envmod.TavernEnv = StubEnv
    contractmod = ModuleType("tavern_ai.contract")
    contractmod.verify_engine = lambda: ENGINE
    modelmod = ModuleType("tavern_ai.model")
    modelmod.TavernExtractor = object
    sb3mod = ModuleType("sb3_contrib")
    class PPO:
        @staticmethod
        def load(*args, **kwargs):
            state["load_calls"] += 1
            raise AssertionError("Deserialization should never occur")
    sb3mod.MaskablePPO = PPO
    for name, module in (("tavern_ai.env", envmod), ("tavern_ai.contract", contractmod),
                         ("tavern_ai.model", modelmod), ("sb3_contrib", sb3mod)):
        monkeypatch.setitem(sys.modules, name, module)
    import tavern_ai
    spec = importlib.util.spec_from_file_location(
        "tavern_ai._isolated_train_test", Path(tavern_ai.__file__).with_name("train.py")
    )
    train = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(train)
    source = tmp_path / "model.zip"
    source.write_bytes(b"corrupted")
    source.with_suffix(".metadata.json").write_text(json.dumps({
        "engine": ENGINE, "total_timesteps": 128,
        "checkpoint_sha256": "0" * 64,
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        train.run(128, 10, tmp_path / "new.zip", resume=source)
    assert state == {"load_calls": 0, "closed": 1}


def test_refuse_wrong_step_count_after_load(monkeypatch, tmp_path):
    state = {"closed": 0}
    envmod = ModuleType("tavern_ai.env")
    class StubEnv:
        def __init__(self, seed): pass
        def close(self): state["closed"] += 1
    envmod.TavernEnv = StubEnv
    contractmod = ModuleType("tavern_ai.contract")
    contractmod.verify_engine = lambda: ENGINE
    modelmod = ModuleType("tavern_ai.model")
    modelmod.TavernExtractor = object
    sb3mod = ModuleType("sb3_contrib")
    class PPO:
        @staticmethod
        def load(*args, **kwargs):
            return type("Loaded", (), {"num_timesteps": 999})()
    sb3mod.MaskablePPO = PPO
    for name, module in (("tavern_ai.env", envmod), ("tavern_ai.contract", contractmod),
                         ("tavern_ai.model", modelmod), ("sb3_contrib", sb3mod)):
        monkeypatch.setitem(sys.modules, name, module)
    import tavern_ai
    spec = importlib.util.spec_from_file_location(
        "tavern_ai._isolated_train_test", Path(tavern_ai.__file__).with_name("train.py")
    )
    train = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(train)
    source = tmp_path / "model.zip"
    source.write_bytes(b"any")
    source.with_suffix(".metadata.json").write_text(json.dumps({
        "engine": ENGINE, "total_timesteps": 128,
        "checkpoint_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="step counters differ"):
        train.run(128, 10, tmp_path / "new.zip", resume=source)
    assert state["closed"] == 1
