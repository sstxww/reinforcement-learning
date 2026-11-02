"""Offline negative/positive tests of the newly required masked inference gate.

Fake models are NOT experimental weights or real-game receipts; the live
Release download + TavernGym probe is a separate Actions run.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tavern_ai import release_asset_verifier as verifier
from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES


class FakeEnv:
    instances = []
    legal_action = 23
    mask_length = ACTIONS
    empty = False

    def __init__(self, seed):
        self.seed = seed
        self.closed = False
        self.steps = []
        self.__class__.instances.append(self)

    def reset(self, *, seed):
        return {"features": "sentinel-features", "cards": "sentinel-cards"}, {}

    def action_masks(self):
        mask = [False] * self.mask_length
        if not self.empty and self.mask_length > self.legal_action:
            mask[self.legal_action] = True
        return mask

    def step(self, action):
        self.steps.append(action)
        assert action == self.legal_action
        return {}, 0.0, False, False, {}

    def close(self):
        self.closed = True


class FakePolicy:
    def __init__(self, action=23):
        self.action = action
        self.seen = None
        self.num_timesteps = 128

    def predict(self, observation, *, action_masks, deterministic):
        self.seen = (observation, list(action_masks), deterministic)
        return self.action, None


@pytest.fixture
def patched_env(monkeypatch):
    import tavern_ai.env
    monkeypatch.setattr(tavern_ai.env, "TavernEnv", FakeEnv)
    FakeEnv.instances.clear()
    FakeEnv.mask_length, FakeEnv.empty, FakeEnv.legal_action = ACTIONS, False, 23
    yield
    FakeEnv.instances.clear()


def test_one_actual_masked_action_and_environment_step(patched_env):
    model = FakePolicy()
    assert verifier._probe_masked_inference(model) == 23
    observation, mask, deterministic = model.seen
    assert observation["features"] == "sentinel-features"
    assert mask[23] is True and sum(mask) == 1
    assert deterministic is True
    assert FakeEnv.instances[-1].steps == [23]
    assert FakeEnv.instances[-1].closed is True


@pytest.mark.parametrize("action", [2, ACTIONS, -1])
def test_mask_illegal_prediction_fails_closed_and_closes(patched_env, action):
    model = FakePolicy(action=action)
    with pytest.raises(ValueError, match="masked-illegal"):
        verifier._probe_masked_inference(model)
    assert FakeEnv.instances[-1].closed
    assert not FakeEnv.instances[-1].steps


@pytest.mark.parametrize("length,empty", [(ACTIONS - 1, False), (ACTIONS, True)])
def test_bad_or_empty_mask_does_not_reach_policy(patched_env, length, empty):
    FakeEnv.mask_length, FakeEnv.empty = length, empty
    model = FakePolicy()
    with pytest.raises(ValueError, match="mask"):
        verifier._probe_masked_inference(model)
    assert model.seen is None
    assert FakeEnv.instances[-1].closed


def _fake_release_fixture(tmp_path, monkeypatch):
    model_id = "synthetic-never-publish"
    weights = tmp_path / "model.zip"
    weights.write_bytes(b"synthetic-unloadable-test-bytes")
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps({
        "schema": 1, "algorithm": "MaskablePPO", "total_timesteps": 128,
        "engine": {"version": "1.1.0", "source_hash": ENGINE_HASH,
                   "features": FEATURES, "cards": CARDS, "actions": ACTIONS}
    }), encoding="utf-8")
    descriptor = lambda path: {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    index = {"assets": [{"id": model_id, "weights": descriptor(weights),
                         "metadata": descriptor(metadata)}]}
    registry = {"candidates": [{"id": model_id, "training_steps": 128}]}
    monkeypatch.setattr(verifier, "validate_asset_index", lambda *_: None)
    monkeypatch.setattr(verifier, "audit_archive", lambda *_: {
        "archive_integrity": "passed", "checkpoint_metadata_schema": 1
    })
    monkeypatch.setattr("tavern_ai.contract.verify_engine", lambda: None)
    policy = FakePolicy()
    class FakeMaskablePPO:
        @staticmethod
        def load(*args, **kwargs):
            assert kwargs["device"] == "cpu"
            return policy
    monkeypatch.setitem(sys.modules, "sb3_contrib",
                        SimpleNamespace(MaskablePPO=FakeMaskablePPO))
    return index, registry, model_id, weights, metadata, policy


def test_verify_local_no_false_cpu_inference_claim(tmp_path, monkeypatch):
    args = _fake_release_fixture(tmp_path, monkeypatch)
    calls = []
    monkeypatch.setattr(verifier, "_probe_masked_inference", lambda policy: calls.append(policy))
    result = verifier.verify_local(*args[:5], check_load=True)
    assert result["sb3_load_checked"] is True
    assert result["masked_legal_inference_checked"] is True
    assert calls == [args[5]]
    assert result["optimizer_resume_checked"] is False
    assert result["complete_game_checked"] is False


def test_failed_probe_must_block_release_restore(tmp_path, monkeypatch):
    args = _fake_release_fixture(tmp_path, monkeypatch)
    def bad_probe(_):
        raise ValueError("Loaded model predicted a masked-illegal action")
    monkeypatch.setattr(verifier, "_probe_masked_inference", bad_probe)
    with pytest.raises(ValueError, match="masked-illegal"):
        verifier.verify_local(*args[:5], check_load=True)


def test_skip_load_never_credits_inference(tmp_path, monkeypatch):
    args = _fake_release_fixture(tmp_path, monkeypatch)
    result = verifier.verify_local(*args[:5], check_load=False)
    assert result["sb3_load_checked"] is False
    assert result["masked_legal_inference_checked"] is False
