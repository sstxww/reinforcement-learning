"""Statistical regression tests; no fake game results substituted for real TavernGym."""
import pytest

from tavern_ai.confirm_buy_s64405d5e import paired_statistics


def make_row(baseline, candidate, interventions=0):
    return {
        "seed": 1,
        "baseline_rank": baseline,
        "candidate_rank": candidate,
        "candidate_interventions": interventions,
    }


def test_paired_deltas_are_candidate_minus_control():
    out = paired_statistics([make_row(8, 6, 4), make_row(7, 8, 2)], draws=400)
    assert out["pairs"] == 2
    assert out["baseline_mean_rank"] == 7.5
    assert out["candidate_mean_rank"] == 7
    assert out["paired_mean_rank_delta"] == -0.5
    assert out["candidate_better_games"] == 1
    assert out["candidate_worse_games"] == 1
    assert out["candidate_interventions"] == 6


def test_constant_paired_difference_bootstrap_is_exact():
    out = paired_statistics([make_row(7, 7), make_row(8, 8)], draws=100)
    assert out["paired_bootstrap_95pct_interval"] == [0, 0]
    assert out["equal_rank_games"] == 2


def test_bootstrap_repeatability():
    rows = [make_row(7, 6), make_row(8, 8), make_row(6, 8)]
    first = paired_statistics(rows, bootstrap_seed=20261102, draws=250)
    second = paired_statistics(rows, bootstrap_seed=20261102, draws=250)
    assert first["paired_bootstrap_95pct_interval"] == second["paired_bootstrap_95pct_interval"]


def test_zero_games_rejected():
    with pytest.raises(ValueError, match="zero paired games"):
        paired_statistics([])
