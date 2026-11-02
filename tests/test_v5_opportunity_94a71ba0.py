"""Pure contract and counter tests; live engine test runs in Actions."""
import numpy as np
import pytest

from tavern_ai.v5_opportunity_94a71ba0 import action_kind, record_action
from tavern_ai.contract import ACTIONS


def make_stats():
    return {"decisions": 0, "buy_legal_decisions": 0, "selected_buys": 0,
            "model_proposed_ends": 0, "model_end_while_buy_legal": 0,
            "guard_forced_ends": 0, "max_identical_action_streak": 0,
            "proposed_action_kinds": {}, "executed_action_kinds": {},
            "raw_action_ids": {}}


def test_end_while_buy_possible_is_distinguished_from_no_buy_opportunity():
    from collections import Counter
    s = make_stats()
    for k in ("proposed_action_kinds", "executed_action_kinds", "raw_action_ids"):
        s[k] = Counter()
    turns = {}
    mask = np.zeros(ACTIONS, dtype=bool)
    mask[[0, 8, 31]] = True
    record_action(s, turns, 2, mask, 0, 0, False, 1)
    assert s["buy_legal_decisions"] == 1
    assert s["model_end_while_buy_legal"] == 1
    assert s["selected_buys"] == 0
    assert s["guard_forced_ends"] == 0
    mask[8] = False
    record_action(s, turns, 3, mask, 0, 0, False, 2)
    assert s["buy_legal_decisions"] == 1
    assert s["model_end_while_buy_legal"] == 1
    assert s["model_proposed_ends"] == 2


def test_guard_and_genuine_buy_are_separate():
    from collections import Counter
    s = make_stats()
    for k in ("proposed_action_kinds", "executed_action_kinds", "raw_action_ids"):
        s[k] = Counter()
    turns = {}
    mask = np.zeros(ACTIONS, dtype=bool)
    mask[[0, 9]] = True
    record_action(s, turns, 4, mask, 9, 9, False, 1)
    record_action(s, turns, 4, mask, 9, 0, True, 2)
    assert (s["selected_buys"], s["guard_forced_ends"], s["max_identical_action_streak"]) == (1, 1, 2)
    assert s["raw_action_ids"]["9"] == 2
    assert turns[4]["selected_buys"] == 1
    assert turns[4]["forced_ends"] == 1


def test_illegal_action_rejected_and_bands_explicit():
    from collections import Counter
    s = make_stats()
    for k in ("proposed_action_kinds", "executed_action_kinds", "raw_action_ids"):
        s[k] = Counter()
    mask = np.zeros(ACTIONS, dtype=bool)
    mask[0] = True
    with pytest.raises(ValueError, match="illegal"):
        record_action(s, {}, 1, mask, 8, 8, False, 1)
    assert action_kind(8) == "buy"
    assert action_kind(22) == "sell"
    assert action_kind(23) == "other"
    assert action_kind(100) == "play"
    assert action_kind(1) == "other"
