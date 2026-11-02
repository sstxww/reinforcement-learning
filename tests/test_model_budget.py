import numpy as np
import pytest

from tavern_ai.reward_match import MAX_ACTIONS_PER_TURN, bounded_action


def mask(*xs):
    result = np.zeros(245, dtype=bool)
    result[list(xs)] = True
    return result


def test_normal_policy_action_remains_unchanged():
    assert bounded_action(mask(0, 3, 9), 9, 2) == (9, False)


def test_budget_prevents_optional_action_loops():
    assert bounded_action(mask(0, 2, 9), 2, MAX_ACTIONS_PER_TURN) == (0, True)


def test_mandatory_choice_without_end_turn():
    assert bounded_action(mask(30, 31), 31, MAX_ACTIONS_PER_TURN) == (30, True)


def test_illegal_action_cannot_be_applied():
    with pytest.raises(ValueError):
        bounded_action(mask(0), 9, 0)
    with pytest.raises(ValueError):
        bounded_action(mask(), 0, 0)
