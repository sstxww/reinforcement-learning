"""Public action-family and opportunity metrics with deliberately synthetic data."""
import pytest
from tavern_ai.action_diagnostics_902968f5 import family, summarize_actions


def test_action_ranges():
    assert family(0) == "end_turn"
    assert family(3) == "upgrade"
    assert family(8) == family(15) == "buy"
    assert family(16) == family(22) == "sell"
    assert family(30) == family(45) == "choose"
    assert family(46) == family(125) == "play"
    assert family(126) == family(195) == "magnetize"
    assert family(244) == "other"


def test_invalid_action():
    with pytest.raises(ValueError):
        family(245)


def test_legal_buy_opportunity_is_not_same_as_buy():
    data = [
        {"family": "end_turn", "legal_buy": True, "same_action_streak": 1,
         "identical_prestate_as_previous": False, "turn": 3},
        {"family": "end_turn", "legal_buy": False, "same_action_streak": 2,
         "identical_prestate_as_previous": False, "turn": 3},
        {"family": "buy", "legal_buy": True, "same_action_streak": 1,
         "identical_prestate_as_previous": True, "turn": 4},
    ]
    x = summarize_actions(data)
    assert x["legal_buy_opportunity_decisions"] == 2
    assert x["actual_buy_actions"] == 1
    assert x["end_turn_when_buy_legal"] == 1
    assert x["end_turn_without_legal_buy"] == 1
    assert x["forced_end_turn_actions"] == 0
    assert x["buy_rate_given_legal_decision"] == 0.5
    assert x["max_same_action_streak"] == 2


def test_empty_trace_never_invents_rate():
    s = summarize_actions([])
    assert s["decisions"] == 0
    assert s["buy_rate_given_legal_decision"] is None
