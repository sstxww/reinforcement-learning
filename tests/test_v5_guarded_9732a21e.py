import numpy as np
import pytest

from tavern_ai.v5_guarded_9732a21e import intervention, MAX_ACTIONS_PER_TURN


def legal(*ids):
    mask = np.zeros(245, dtype=bool)
    mask[list(ids)] = True
    return mask


def test_buy_priority_only_when_a_buy_is_legal():
    assert intervention(2, legal(0, 2, 8), 2, 0) == (8, "buy_priority")
    assert intervention(2, legal(0, 2), 2, 0) == (2, "none")
    assert intervention(8, legal(0, 8), 2, 0) == (8, "none")


def test_forced_buys_capped_per_turn():
    assert intervention(2, legal(0, 2, 8), 4, 2) == (2, "none")
    assert intervention(2, legal(0, 2, 8), 4, 1) == (8, "buy_priority")


def test_no_forced_illegal_end_turn():
    assert intervention(7, legal(7, 8), MAX_ACTIONS_PER_TURN, 2) == (7, "none")
    assert intervention(7, legal(0, 7, 8), MAX_ACTIONS_PER_TURN, 2) == (0, "turn_budget")
    assert intervention(0, legal(0, 7), MAX_ACTIONS_PER_TURN, 2) == (0, "none")


def test_mandatory_choose_not_overridden():
    assert intervention(30, legal(0, 8, 30), MAX_ACTIONS_PER_TURN, 0) == (30, "none")


def test_illegal_model_action_or_mask_fails():
    with pytest.raises(ValueError):
        intervention(4, legal(0, 8), 0, 0)
    with pytest.raises(ValueError):
        intervention(0, np.zeros(245, dtype=bool), 0, 0)
    with pytest.raises(ValueError):
        intervention(245, legal(0), 0, 0)
