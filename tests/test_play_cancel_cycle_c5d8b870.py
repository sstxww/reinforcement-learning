"""Synthetic fixtures only; no generated test data is a real TavernGym match."""
import pytest
from tavern_ai.play_cancel_cycle_c5d8b870 import CycleTrace


def mask(*actions):
    m = [False] * 245
    for action in actions:
        m[action] = True
    return m


def test_exact_return_and_repeated_second_cycle():
    t = CycleTrace()
    m = mask(7, 50, 8)
    t.record(3, 50, m, b'A', b'B')
    t.record(3, 7, m, b'B', b'A')
    t.record(3, 50, m, b'A', b'B')
    t.record(3, 7, m, b'B', b'A')
    c = t.report()['counters']
    assert c['adjacent_play_cancel_pairs'] == 2
    assert c['exact_public_state_return_pairs'] == 2
    assert c['repeated_exact_state_return_pairs'] == 1
    assert c['legal_buy_decisions'] == 4
    assert c['chosen_buy_decisions'] == 0


def test_nonreturn_or_transition_discontinuity_not_counted():
    t = CycleTrace()
    m = mask(7, 50)
    t.record(2, 50, m, b'A', b'B')
    t.record(2, 7, m, b'not-B', b'A')
    assert t.report()['counters']['adjacent_play_cancel_pairs'] == 1
    assert t.report()['counters']['exact_public_state_return_pairs'] == 0


def test_turn_break_and_intervening_action_reset():
    t = CycleTrace()
    m = mask(7, 50, 1)
    t.record(2, 50, m, b'A', b'B')
    t.record(3, 7, m, b'B', b'A')
    t.record(3, 50, m, b'A', b'B')
    t.record(3, 1, m, b'B', b'C')
    t.record(3, 7, m, b'C', b'A')
    assert t.report()['counters']['adjacent_play_cancel_pairs'] == 0


def test_no_claim_when_after_unavailable():
    t = CycleTrace()
    m = mask(7, 50)
    t.record(3, 50, m, b'A', None)
    t.record(3, 7, m, b'B', b'A')
    assert t.report()['counters']['adjacent_play_cancel_pairs'] == 1
    assert t.report()['counters']['exact_public_state_return_pairs'] == 0


def test_reject_invalid_mask_and_raw_illegal():
    t = CycleTrace()
    with pytest.raises(ValueError):
        t.record(2, 50, mask(7), b'A', b'B')
    with pytest.raises(ValueError):
        t.record(2, 50, [True] * 244, b'A', b'B')
    with pytest.raises(ValueError):
        t.record(2.0, 50, mask(50), b'A', b'B')
    with pytest.raises(TypeError):
        t.record(2, 50, mask(50), 'not-bytes', b'B')
