"""Synthetic ONLY: validation tests, not match evidence."""
from copy import deepcopy

import pytest

from tavern_ai.paired_rank_gate_a280d7eb import summarize
from tavern_ai.contract import ENGINE_HASH


def receipt(seed, rank, policy, *, seat=0):
    placement = [rank] + [i for i in range(1, 9) if i != rank]
    return {
        "schema": 1, "environment": "TavernGym", "completed": True,
        "engine_version": "1.1.0", "engine_source_hash": ENGINE_HASH,
        "agent_id": "synthetic-fixture-only", "seed": seed, "seat": seat,
        "policy": policy, "model_sha256": "a" * 64 if policy == "model" else None,
        "placements": placement, "turns": 10, "decisions": 35,
        "truncated_combats": 0, "turn_limit_end": False,
    }


def pair():
    return ([receipt(99001, 5, "model"), receipt(99002, 8, "model")],
            [receipt(99001, 7, "baseline"), receipt(99002, 8, "baseline")])


def test_exact_seed_seat_paired_descriptive_only():
    m, b = pair()
    report = summarize(m, b)
    assert report["paired_games"] == 2
    assert report["paired_mean_rank_delta"] == -1
    assert report["model_mean_rank"] == 6.5
    assert report["baseline_mean_rank"] == 7.5
    assert report["model_top4_rate"] == 0
    assert report["promotion_allowed"] is False
    assert report["strength_gain_proven"] is False
    assert report["pairs"][0]["delta_model_minus_baseline"] == -2
    assert report["bootstrap_95pct_descriptive_interval"][0] <= 0


@pytest.mark.parametrize("guard", [
    {"guard_forced_ends": 1},
    {"model_guard_forced_end": 1},
    {"fallback_count": 2},
    {"safety_fallbacks": 1},
    {"guarded": True},
    {"raw_model_only": False},
])
def test_never_treat_assisted_result_as_raw(guard):
    m, b = pair()
    m[0].update(guard)
    with pytest.raises(ValueError, match="Guarded"):
        summarize(m, b)


def test_strict_receipt_permutation_mandatory():
    m, b = pair()
    m[0]["placements"] = [1, 1, 3, 4, 5, 6, 7, 8]
    with pytest.raises(ValueError, match="permutation"):
        summarize(m, b)


def test_duplicate_seed_and_seat_rejected():
    m, b = pair()
    with pytest.raises(ValueError, match="Duplicate"):
        summarize(m + [deepcopy(m[0])], b)


def test_unmatched_seed_or_seat_rejected():
    m, b = pair()
    b[1]["seat"] = 1
    with pytest.raises(ValueError, match="coverage"):
        summarize(m, b)


def test_mixed_model_sha_rejected():
    m, b = pair()
    m[1]["model_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="Different checkpoint"):
        summarize(m, b)


def test_wrong_engine_or_unverified_policy_rejected():
    m, b = pair()
    m[0]["engine_source_hash"] = "deadbeef"
    with pytest.raises(ValueError, match="source fingerprint"):
        summarize(m, b)
    m, b = pair()
    m[0]["policy"] = "guarded_model"
    with pytest.raises(ValueError, match="policy"):
        summarize(m, b)


def test_bad_bootstrap_budget_rejected():
    m, b = pair()
    with pytest.raises(ValueError, match="bootstrap"):
        summarize(m, b, bootstrap_samples=10)


def test_empty_input_rejected():
    with pytest.raises(ValueError, match="At least one"):
        summarize([], [])


def test_controlled_seat_conflict_rejected():
    m, b = pair()
    m[0]["controlled_seat"] = 2
    with pytest.raises(ValueError, match="Conflicting"):
        summarize(m, b)
