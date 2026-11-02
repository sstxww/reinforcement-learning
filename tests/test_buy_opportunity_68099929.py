"""Never confuse missing buys with missing legal opportunities."""
import pytest

from tavern_ai.buy_opportunity_68099929 import classify, summary_from_decisions


def event(turn, action, legal, state):
    return {"turn": turn, "action": action, "buy_legal": legal,
            "state_hash": state, "same_public_state_as_prior": False}


def test_action_semantics_are_pinned():
    assert classify(0) == "end_turn"
    assert classify(8) == "buy"
    assert classify(15) == "buy"
    assert classify(3) == "upgrade"
    assert classify(30) == "choose"
    assert classify(46) == "play"
    assert classify(16) == "sell"


def test_end_turn_with_legal_buy_is_counted_separately():
    items = [event(2, 0, True, "a"), event(3, 8, True, "b"),
             event(3, 0, False, "c"), event(4, 0, True, "d")]
    result = summary_from_decisions(items)
    assert result["buy_chosen"] == 1
    assert result["buy_legal_decisions"] == 3
    assert result["end_while_buy_legal"] == 2
    assert result["turns_with_end_while_buy_legal"] == 2
    assert result["conditional_buy_rate_given_legal"] == pytest.approx(1 / 3)
    assert result["conditional_end_rate_given_legal_buy"] == pytest.approx(2 / 3)
    assert result["all_end_turns"] == 3


def test_zero_buy_with_zero_legal_opportunities_is_not_misreported():
    result = summary_from_decisions([event(1, 0, False, "x"), event(2, 0, False, "y")])
    assert result["buy_chosen"] == 0
    assert result["buy_legal_decisions"] == 0
    assert result["conditional_buy_rate_given_legal"] is None
    assert result["end_while_buy_legal"] == 0


def test_identical_public_state_and_turn_independence():
    items = [event(2, 1, True, "x"), event(2, 8, True, "x"),
             event(3, 0, True, "z")]
    items[1]["same_public_state_as_prior"] = True
    result = summary_from_decisions(items)
    assert result["consecutive_identical_public_observation"] == 1
    assert result["unique_public_states_with_legal_buy"] == 2
    assert result["distinct_turns_with_legal_buy"] == 2


def test_invalid_opportunity_record_rejected():
    with pytest.raises(ValueError):
        summary_from_decisions([])
    with pytest.raises(ValueError):
        summary_from_decisions([event(1, True, True, "x")])
    with pytest.raises(ValueError):
        summary_from_decisions([event(-1, 0, True, "x")])
