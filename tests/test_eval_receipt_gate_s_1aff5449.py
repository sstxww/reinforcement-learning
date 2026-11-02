"""Offline negative tests use synthetic receipts, never actual game evidence."""
from __future__ import annotations

from copy import deepcopy

import pytest

import tavern_ai.evaluate as evaluation
from tavern_ai.contract import ENGINE_HASH


def receipt(seed: int, *, policy: str = "baseline", model_hash: str | None = None) -> dict:
    return {
        "schema": 1, "environment": "TavernGym", "completed": True,
        "agent_id": "evaluation", "policy": policy,
        "placements": [1, 2, 3, 4, 5, 6, 7, 8],
        "turns": 13, "decisions": 64, "seed": seed,
        "engine_version": "1.1.0", "engine_source_hash": ENGINE_HASH,
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": model_hash,
    }


def test_validates_paired_seed_and_model_digest_before_reporting(tmp_path, monkeypatch):
    model = tmp_path / "fake-model-only-for-mock.zip"
    model.write_bytes(b"synthetic-not-a-real-checkpoint")
    seen = []

    def fake_game(seed, agent_id, policy, model_path=None):
        seen.append((seed, policy))
        return receipt(seed, policy=policy, model_hash=("a" * 64 if policy == "model" else None))

    monkeypatch.setattr(evaluation, "run", fake_game)
    report = evaluation.evaluate("model", model, games=3, start_seed=91200, compare_baseline=True)
    assert seen == [(91200, "model"), (91201, "model"), (91202, "model"),
                    (91200, "baseline"), (91201, "baseline"), (91202, "baseline")]
    assert report["candidate"]["games"] == report["baseline"]["games"] == 3
    assert report["controlled_seat"] == 0
    assert report["model_evidence_mode"].startswith("raw model")


@pytest.mark.parametrize("change", [
    lambda row: row.update(completed=False),
    lambda row: row.update(placements=[1] * 8),
    lambda row: row.update(engine_source_hash="wrong"),
    lambda row: row.update(seed=9000),
    lambda row: row.update(policy="model", model_sha256="a" * 64),
    lambda row: row.update(guard_forced_ends=1),
    lambda row: row.update(fallback_actions=1),
    lambda row: row.update(truncated_combats=1),
    lambda row: row.update(seat=2),
])
def test_rejects_fabricated_or_incompatible_evidence(change):
    candidate = receipt(91200)
    change(candidate)
    with pytest.raises(ValueError):
        evaluation._verify_full_game_records([candidate], "baseline", [91200])


def test_rejects_inconsistent_model_weights():
    rows = [receipt(91200, policy="model", model_hash="a" * 64),
            receipt(91201, policy="model", model_hash="b" * 64)]
    with pytest.raises(ValueError, match="weight hashes"):
        evaluation._verify_full_game_records(rows, "model", [91200, 91201])


def test_rejects_missing_or_duplicate_seed_receipts():
    rows = [receipt(91200), receipt(91200)]
    with pytest.raises(ValueError, match="seed"):
        evaluation._verify_full_game_records(rows, "baseline", [91200, 91201])
    with pytest.raises(ValueError, match="Missing"):
        evaluation._verify_full_game_records(rows[:1], "baseline", [91200, 91201])


def test_empty_summary_fails_closed():
    with pytest.raises(ValueError, match="zero games"):
        evaluation.summarize([])
