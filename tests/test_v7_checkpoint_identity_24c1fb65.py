"""Synthetic negative tests for active-checkpoint/receipt SHA binding.

Mock receipts below are NOT real TavernGym games and must not be archived as such.
"""
import hashlib

import pytest

import tavern_ai.evaluate as evaluation
from tavern_ai.contract import ENGINE_HASH


def _fake(seed: int, digest: str) -> dict:
    return {
        "schema": 1, "environment": "TavernGym", "completed": True,
        "agent_id": "evaluation", "policy": "model", "seed": seed,
        "turns": 12, "decisions": 54,
        "placements": [8, 1, 2, 3, 4, 5, 6, 7],
        "truncated_combats": 0, "turn_limit_end": False,
        "engine_version": "1.1.0", "engine_source_hash": ENGINE_HASH,
        "model_sha256": digest,
    }


def test_consistent_foreign_model_receipts_are_rejected(tmp_path, monkeypatch):
    """Previously two mutually consistent but unrelated model hashes passed."""
    checkpoint = tmp_path / "mock.zip"
    checkpoint.write_bytes(b"synthetic-checkpoint-A-not-a-real-model")
    wrong_sha = hashlib.sha256(b"synthetic-checkpoint-B").hexdigest()
    assert wrong_sha != hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    monkeypatch.setattr(evaluation, "run", lambda seed, *_: _fake(seed, wrong_sha))
    with pytest.raises(ValueError, match="does not match evaluated checkpoint"):
        evaluation.evaluate("model", checkpoint, games=2, start_seed=97520)


def test_matching_checkpoint_receipts_pass_mock_gate(tmp_path, monkeypatch):
    checkpoint = tmp_path / "mock.zip"
    checkpoint.write_bytes(b"synthetic-model-A")
    correct_sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    monkeypatch.setattr(evaluation, "run", lambda seed, *_: _fake(seed, correct_sha))
    result = evaluation.evaluate("model", checkpoint, games=2, start_seed=97530)
    assert result["candidate"]["games"] == 2
    assert result["candidate"]["placements"] == [8, 8]


def test_checkpoint_replacement_during_match_is_rejected(tmp_path, monkeypatch):
    checkpoint = tmp_path / "mock.zip"
    checkpoint.write_bytes(b"synthetic-original")
    original_sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()

    def switched_model(seed, *_args):
        checkpoint.write_bytes(b"synthetic-replaced")
        return _fake(seed, original_sha)

    monkeypatch.setattr(evaluation, "run", switched_model)
    with pytest.raises(ValueError, match="changed during evaluation"):
        evaluation.evaluate("model", checkpoint, games=1, start_seed=97540)
