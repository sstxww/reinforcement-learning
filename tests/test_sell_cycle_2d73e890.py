import numpy as np
import pytest
from tavern_ai.sell_cycle_2d73e890 import SellCyclePolicy

def obs(*actions):
    m = np.zeros(245, dtype=bool)
    m[list(actions)] = True
    return {"action_mask": m}

def test_buy_then_sell_when_blocked():
    p = SellCyclePolicy()
    assert p.act(obs(0, 8, 16), {"turn": 4}) == 8
    assert p.act(obs(0, 16, 17), {"turn": 4}) == 16
    assert p.total_sells == 1

def test_no_premature_or_double_sale():
    p = SellCyclePolicy()
    assert p.act(obs(0, 16), {"turn": 4}) == 0
    assert p.act(obs(0, 8, 16), {"turn": 5}) == 8
    assert p.act(obs(0, 16), {"turn": 5}) == 16
    assert p.act(obs(0, 8, 16), {"turn": 5}) == 8
    assert p.act(obs(0, 16), {"turn": 5}) == 0

def test_pending_choice_and_magnetize_prevent_sale():
    p = SellCyclePolicy()
    assert p.act(obs(0, 8, 16), {"turn": 1}) == 8
    assert p.act(obs(0, 16, 30), {"turn": 1}) == 30
    assert p.act(obs(0, 16, 126), {"turn": 1}) == 126
    assert p.total_sells == 0

def test_turn_resets_sale_budget():
    p = SellCyclePolicy()
    for turn in (2, 3):
        assert p.act(obs(0, 8, 16), {"turn": turn}) == 8
        assert p.act(obs(0, 16), {"turn": turn}) == 16
    assert p.total_sells == 2

def test_zero_budget_matches_baseline():
    p = SellCyclePolicy(budget=0)
    assert p.act(obs(0, 8, 16), {"turn": 3}) == 8
    assert p.act(obs(0, 16), {"turn": 3}) == 0

def test_explicit_baseline_guard_not_learned():
    p = SellCyclePolicy()
    assert p.act(obs(0, 8, 16), {"turn": 3, "actions_used": 85}) == 0
    assert p.forced_ends == 1
    assert p.total_sells == 0

def test_bad_input():
    with pytest.raises(ValueError):
        SellCyclePolicy(budget=3)
    with pytest.raises(ValueError):
        SellCyclePolicy().act(obs(), {"turn": 1})
