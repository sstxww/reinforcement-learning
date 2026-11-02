"""R002 offline metric regression tests, no fake match receipts."""
import pytest

torch = pytest.importorskip("torch", reason="official BC requires optional torch")

from tavern_ai.bc_official_session_661adf61 import histogram, paired_stats


def sample(action):
    return (None, None, None, action)


def test_action_bands_are_exactly_partitioned():
    counts = histogram([sample(0), sample(8), sample(16), sample(23),
                        sample(30), sample(45), sample(46), sample(125),
                        sample(126), sample(195), sample(196), sample(244)])
    assert counts["buy"] == 1
    assert counts["sell"] == 1
    assert counts["magnetize"] == 2
    assert counts["move"] == 2
    assert counts["choose"] == 2
    assert sum(counts.values()) == 12


def test_paired_stats_do_not_include_incomplete_games():
    cand = [{"seed": 1, "completed": True, "placements": [3]},
            {"seed": 2, "completed": False, "reason": "raw_turn_budget_exceeded"}]
    baseline = [{"seed": 1, "completed": True, "placements": [5]},
                {"seed": 2, "completed": True, "placements": [8]}]
    result = paired_stats(cand, baseline)
    assert result["paired_completed"] == 1
    assert result["per_seed_rank_delta"] == [-2]
    assert result["paired_seeds"] == [1]


def test_no_paired_success_cannot_be_reported_as_gain():
    result = paired_stats([{"seed": 1, "completed": False}],
                          [{"seed": 1, "completed": True, "placements": [8]}])
    assert result["mean_rank_delta"] is None
    assert result["paired_completed"] == 0
