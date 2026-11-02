import numpy as np
import pytest

from tavern_ai.rank8_probe_decfc670 import classify, decide_with_guard, TURN_BUDGET


def test_action_family_ranges_are_conservative():
    assert classify(0) == "end_turn"
    assert classify(3) == "upgrade"
    assert classify(8) == "buy"
    assert classify(15) == "buy"
    assert classify(16) == "sell"
    assert classify(22) == "sell"
    assert classify(46) == "play"
    assert classify(125) == "play"
    assert classify(127) == "other"


def test_forced_end_is_never_mislabeled_as_model_decision():
    mask = np.zeros(245, dtype=bool)
    mask[0] = True
    mask[8] = True
    assert decide_with_guard(mask, None, TURN_BUDGET) == (0, True)
    assert decide_with_guard(mask, 8, TURN_BUDGET - 1) == (8, False)
    assert decide_with_guard(mask, 0, TURN_BUDGET - 1) == (0, False)


def test_illegal_predictions_and_nonendable_budget_are_rejected():
    mask = np.zeros(245, dtype=bool)
    mask[8] = True
    with pytest.raises(ValueError, match="illegal"):
        decide_with_guard(mask, 0, 0)
    with pytest.raises(ValueError, match="illegal"):
        decide_with_guard(mask, 245, 0)
    with pytest.raises(RuntimeError, match="END_TURN"):
        decide_with_guard(mask, None, TURN_BUDGET)
