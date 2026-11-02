import numpy as np
from tavern_ai.freeze_exit_s_717d0e50 import select_action


def mask(*actions):
    result = np.zeros(245, dtype=bool)
    result[list(actions)] = True
    return result


def test_one_freeze_before_end_turn():
    m = mask(0, 2)
    assert select_action(m, 5, 4, False, True) == 2
    assert select_action(m, 5, 5, True, True) == 0
    assert select_action(m, 5, 4, False, False) == 0


def test_never_freezes_at_action_guard_or_outside_range():
    m = mask(0, 2)
    assert select_action(m, 5, 85, False, True) == 0
    assert select_action(m, 3, 4, False, True) == 0
    assert select_action(m, 10, 4, False, True) == 0


def test_no_freeze_when_refresh_or_buy_legal():
    assert select_action(mask(0, 1, 2), 5, 4, False, True) == 0
    assert select_action(mask(0, 2, 8), 5, 4, False, True) == 8


def test_mandatory_choose_never_overridden():
    assert select_action(mask(30, 31), 5, 4, False, True) == 30


def test_freeze_is_always_mask_legal():
    m = mask(0)
    assert select_action(m, 5, 4, False, True) == 0
