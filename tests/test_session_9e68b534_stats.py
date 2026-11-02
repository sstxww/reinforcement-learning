import pytest
from tavern_ai.session_9e68b534_stats import (
    bootstrap_mean_interval, paired_summary, solo_summary, wilson_interval,
)


def record(seed, rank):
    return {"environment": "TavernGym", "completed": True, "seed": seed,
            "placements": [rank] + [x for x in range(1, 9) if x != rank]}


def test_wilson_preserves_uncertainty_at_extremes():
    assert wilson_interval(0, 3)[1] > 0.5
    assert wilson_interval(3, 3)[0] < 0.5
    assert wilson_interval(2, 4) == pytest.approx([0.15003899, 0.84996101])


def test_bootstrap_reproducible_by_seed():
    a = bootstrap_mean_interval([2, 4, 8, 3], seed=6)
    assert a == bootstrap_mean_interval([2, 4, 8, 3], seed=6)
    assert a[0] <= 4.25 <= a[1]
    assert bootstrap_mean_interval([5, 5, 5]) == [5, 5]


def test_solo_summary_counts_unique_complete_games_only():
    result = solo_summary([record(24, 7), record(22, 1), record(23, 4)])
    assert result["seeds"] == [22, 23, 24]
    assert result["ranks"] == [1, 4, 7]
    assert result["top4_rate"] == pytest.approx(2 / 3)
    assert result["first_place_rate"] == pytest.approx(1 / 3)
    assert result["insufficient_for_strength_claim"] is True
    with pytest.raises(ValueError, match="Duplicate seed"):
        solo_summary([record(1, 3), record(1, 4)])


def test_invalid_or_incomplete_receipts_rejected():
    bad = record(1, 1)
    bad["placements"] = [1, 1, 2, 3, 4, 5, 6, 7]
    with pytest.raises(ValueError, match="permutation"):
        solo_summary([bad])
    with pytest.raises(ValueError, match="incomplete"):
        solo_summary([dict(record(1, 3), completed=False)])


def test_paired_comparison_uses_exactly_same_seeds():
    control = [record(11, 7), record(12, 6), record(13, 6)]
    candidate = [record(13, 4), record(12, 5), record(11, 5)]
    result = paired_summary(candidate, control)
    assert result["paired_rank_deltas"] == [-2, -1, -2]
    assert result["candidate_minus_control_mean_rank"] == pytest.approx(-5 / 3)
    assert result["paired_bootstrap_95pct"][1] <= -1
    with pytest.raises(ValueError, match="identical seed"):
        paired_summary(candidate, control[:-1])
