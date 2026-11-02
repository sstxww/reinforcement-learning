"""Synthetic-only negative contract tests: not game receipts or win evidence."""
from copy import deepcopy
import pytest

from tavern_ai.paired_receipt_gate_v5 import compare


def make_row(seed=100, seat=0, rank=8, policy="baseline", guarded=False):
    positions = list(range(1, 9))
    positions[seat], positions[positions.index(rank)] = rank, positions[seat]
    return {
        "schema": 1, "environment": "TavernGym", "completed": True,
        "engine_version": "1.1.0", "engine_source_hash": "6d8712c93022ba11",
        "agent_id": "synthetic-test-only", "policy": policy,
        "seed": seed, "seat": seat, "turns": 13, "decisions": 60,
        "placements": positions, "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": "a" * 64 if policy != "baseline" else None,
        "guarded": guarded,
    }


def test_good_pair_no_promotion_and_too_small_for_ci():
    candidate = [make_row(seed=301, rank=4, policy="model")]
    baseline = [make_row(seed=301, rank=7)]
    report = compare(candidate, baseline)
    assert report["games_per_arm"] == 1
    assert report["paired_mean_placement_delta"] == -3
    assert report["paired_bootstrap_95pct_interval"] is None
    assert report["model_promotion_authorized"] is False
    assert report["evidence_status"] == "insufficient_evidence"


def test_equal_twenty_pairs_never_become_gain():
    candidate = [make_row(seed=i, rank=8, policy="model") for i in range(20)]
    baseline = [make_row(seed=i, rank=8) for i in range(20)]
    result = compare(candidate, baseline, draws=100)
    assert result["paired_bootstrap_95pct_interval"] == [0.0, 0.0]
    assert result["evidence_status"] == "insufficient_evidence"


def test_guarded_game_is_diagnostic_only_even_when_rank_better():
    c = [make_row(seed=12, rank=1, policy="model_guarded", guarded=True)]
    b = [make_row(seed=12, rank=8)]
    result = compare(c, b)
    assert result["guarded_candidate_games"] == 1
    assert result["evidence_status"] == "diagnostic_guarded_not_promotable"


@pytest.mark.parametrize("field,value", [
    ("completed", False), ("engine_source_hash", "wrong"),
    ("turn_limit_end", True), ("truncated_combats", 1),
    ("seed", True), ("seat", 8),
    ("placements", [1] * 8), ("model_sha256", "bad"),
])
def test_invalid_candidate_rejected(field, value):
    c = make_row(policy="model")
    c[field] = value
    with pytest.raises(ValueError):
        compare([c], [make_row()])


def test_undeclared_fallback_rejected():
    c = make_row(policy="model")
    c["fallback_count"] = 2
    with pytest.raises(ValueError, match="Undisclosed"):
        compare([c], [make_row()])


def test_unpaired_seeds_rejected():
    with pytest.raises(ValueError, match="identical"):
        compare([make_row(seed=12, policy="model")], [make_row(seed=13)])


def test_duplicate_pairs_rejected():
    c = make_row(policy="model")
    with pytest.raises(ValueError, match="Duplicate"):
        compare([c, deepcopy(c)], [make_row()])


def test_mismatched_model_hashes_rejected():
    c1 = make_row(seed=100, policy="model")
    c2 = make_row(seed=101, policy="model")
    c2["model_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="SHA changes"):
        compare([c1, c2], [make_row(seed=100), make_row(seed=101)])


def test_seat_mismatch_rejected():
    c = make_row(policy="model", seat=2, rank=3)
    c["agent_placement"] = 7
    with pytest.raises(ValueError, match="Seat/rank"):
        compare([c], [make_row(seat=2, rank=8)])


def test_bad_bootstrap_budget_rejected():
    with pytest.raises(ValueError, match="draws"):
        compare([make_row(policy="model")], [make_row()], draws=5)
