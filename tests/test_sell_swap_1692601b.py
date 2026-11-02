import numpy as np
from tavern_ai.sell_swap_1692601b import SellSwapPolicy

def obs(*legal):
    m = np.zeros(245, dtype=bool)
    m[list(legal)] = True
    return {"action_mask": m}

BOARD = tuple(range(16, 23))
CTX = lambda t, n=0: {"turn": t, "actions_used": n}

def test_guard_full_board_and_affordable_buy():
    p = SellSwapPolicy(7, "last")
    assert p.act(obs(0, 8, *range(16, 22)), CTX(9)) == 8
    assert p.act(obs(0, *BOARD), CTX(9)) == 0
    assert p.sales == 0

def test_turn_gate_and_followup_buy():
    p = SellSwapPolicy(7, "last")
    m = obs(0, 8, *BOARD)
    assert p.act(m, CTX(6)) == 8
    assert p.act(m, CTX(7)) == 22
    assert p.act(obs(0, 9), CTX(7, 1)) == 9
    assert p.sales == 1 and p.buys == 1
    assert p.act(m, CTX(7, 2)) == 8

def test_choice_play_and_budget_gates():
    p = SellSwapPolicy(7, "first")
    assert p.act(obs(0, 8, 46, *BOARD), CTX(10)) == 46
    assert p.act(obs(0, 8, 30, *BOARD), CTX(10)) == 30
    assert p.act(obs(0, 8, *BOARD), CTX(10, 50)) == 8
    assert p.act(obs(0, 8, *BOARD), CTX(10, 1)) == 16

def test_orphaned_sell_is_reported():
    p = SellSwapPolicy(7, "last")
    assert p.act(obs(0, 8, *BOARD), CTX(8)) == 22
    assert p.act(obs(0), CTX(8, 1)) == 0
    assert p.orphans == 1
