"""Pure-metric checks; full simulator coverage is provided by the session workflow."""
import pytest
from tavern_ai.entropy_trial import summarize


def receipt(rank: int, decisions: int = 15) -> dict:
    return {"placements": [rank], "decisions": decisions, "truncated_combats": 0}


def test_paired_aggregate():
    s = summarize([receipt(2, 10), receipt(6, 20)])
    assert s["games"] == 2
    assert s["mean_placement"] == 4
    assert s["top4_rate"] == 0.5
    assert s["first_rate"] == 0
    assert s["mean_decisions"] == 15


def test_empty_metrics_fails():
    with pytest.raises(ValueError, match="full match"):
        summarize([])
