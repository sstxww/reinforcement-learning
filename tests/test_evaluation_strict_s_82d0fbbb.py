"""Regression gate: no incomplete, assisted or mismatched match enters official evaluator."""
import hashlib
import pytest
from tavern_ai import evaluate as evaluation
from tavern_ai.contract import ENGINE_HASH

def receipt(seed=11, policy="baseline", model_sha=None):
    return {
        "schema": 1, "environment": "TavernGym", "engine_version": "1.1.0",
        "engine_source_hash": ENGINE_HASH, "agent_id": "evaluation",
        "policy": policy, "seed": seed, "completed": True,
        "turns": 15, "decisions": 41, "placements": list(range(1, 9)),
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": model_sha,
    }

def test_valid_baseline_full_game_is_scored(monkeypatch):
    monkeypatch.setattr(evaluation, "run", lambda seed, agent_id, policy, model=None:
                        receipt(seed=seed, policy=policy))
    result = evaluation.evaluate("baseline", None, 2, 11)
    assert result["candidate"]["games"] == 2
    assert result["receipt_gate"] == "strict_unassisted_full_match"

@pytest.mark.parametrize("mutation", [
    {"completed": False},
    {"placements": [1, 1, 2, 3, 4, 5, 6, 7]},
    {"engine_source_hash": "unmatched"},
    {"policy": "model"},
    {"seed": 999},
    {"guard_forced_ends": 1},
    {"raw_model_only": False},
    {"turn_limit_end": True},
])
def test_invalid_or_assisted_receipt_fails_closed(monkeypatch, mutation):
    case = receipt()
    case.update(mutation)
    monkeypatch.setattr(evaluation, "run", lambda *args, **kwargs: case)
    with pytest.raises(ValueError):
        evaluation.evaluate("baseline", None, 1, 11)

def test_model_digest_cannot_be_swapped(monkeypatch, tmp_path):
    archive = tmp_path / "candidate.zip"
    archive.write_bytes(b"synthetic unit-test bytes, not PPO weights")
    bad = receipt(policy="model", model_sha="0" * 64)
    monkeypatch.setattr(evaluation, "run", lambda *args, **kwargs: bad)
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        evaluation.evaluate("model", archive, 1, 11)

def test_model_receipt_matches_request(monkeypatch, tmp_path):
    archive = tmp_path / "candidate.zip"
    archive.write_bytes(b"synthetic digest-only fixture; no simulated game")
    model_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    monkeypatch.setattr(evaluation, "run", lambda seed, agent_id, policy, model=None:
                        receipt(seed=seed, policy=policy, model_sha=model_sha))
    result = evaluation.evaluate("model", archive, 1, 11)
    assert result["candidate_model_sha256"] == model_sha
    assert result["candidate"]["mean_placement"] == 1
