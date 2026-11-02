"""Offline regression: the canonical evaluator rejects non-genuine pairings."""
import hashlib
import importlib

import pytest

module = importlib.import_module("tavern_ai.evaluate")


def game(seed, policy, *, rank=8, model_sha=None, **change):
    ranks = list(range(1, 9))
    ranks.remove(rank)
    ranks.insert(0, rank)
    data = {
        "seed": seed, "agent_id": "evaluation", "policy": policy,
        "completed": True, "engine_source_hash": "6d8712c93022ba11",
        "engine_version": "1.1.0", "placements": ranks, "decisions": 100,
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": model_sha,
    }
    data.update(change)
    return data


def test_matched_raw_model_and_baseline_reports_bounded_uncertainty(monkeypatch, tmp_path):
    model = tmp_path / "model.zip"
    model.write_bytes(b"unit test fixture only; not real model weights")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()

    def fake(seed, agent_id, policy, path=None):
        return game(seed, policy, rank=4 if policy == "model" else 6,
                    model_sha=digest if policy == "model" else None)

    monkeypatch.setattr(module, "run", fake)
    result = module.evaluate("model", model, 3, 71000, compare_baseline=True)
    assert result["candidate"]["games"] == 3
    assert result["paired_sample_size"] == 3
    assert result["paired_rank_deltas_candidate_minus_baseline"] == [-2, -2, -2]
    assert result["paired_mean_placement_delta"] == -2
    assert result["paired_mean_delta_95pct_hoeffding_bounds"][0] <= 0
    assert result["paired_mean_delta_95pct_hoeffding_bounds"][1] >= 0
    assert result["fallback_allowed"] is False
    assert result["model_sha256"] == digest


@pytest.mark.parametrize("change", [
    {"completed": False}, {"turn_limit_end": True}, {"truncated_combats": 1},
    {"placements": [8] * 8}, {"guard_forced_ends": 1},
    {"raw_model_only": False}, {"safety_fallback_count": 1},
    {"policy": "guarded_model"}, {"engine_source_hash": "different"},
    {"decisions": 0}, {"model_sha256": None},
])
def test_reject_unverified_model_game(monkeypatch, tmp_path, change):
    model = tmp_path / "model.zip"
    model.write_bytes(b"test bytes")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()

    def modified(seed, agent_id, policy, path=None):
        record = game(seed, policy, model_sha=digest)
        record.update(change)
        return record

    monkeypatch.setattr(module, "run", modified)
    with pytest.raises(ValueError):
        module.evaluate("model", model, 1, 71001)


def test_baseline_contamination_or_seed_drift_is_rejected(monkeypatch, tmp_path):
    model = tmp_path / "model.zip"
    model.write_bytes(b"test bytes")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()

    def bad_baseline(seed, agent_id, policy, path=None):
        if policy == "model":
            return game(seed, policy, model_sha=digest)
        return game(seed + 1, "baseline", model_sha=None)

    monkeypatch.setattr(module, "run", bad_baseline)
    with pytest.raises(ValueError, match="Seed"):
        module.evaluate("model", model, 1, 71002, compare_baseline=True)


def test_no_unearned_strength_claim_for_single_pair():
    paired = module.paired_statistics([game(1, "model", rank=1)],
                                      [game(1, "baseline", rank=8)])
    assert paired["paired_mean_delta_95pct_hoeffding_bounds"] == [-7.0, 7.0]
    assert paired["paired_sample_size"] == 1
    with pytest.raises(ValueError, match="seeds"):
        module.paired_statistics([game(1, "model")], [game(2, "baseline")])
