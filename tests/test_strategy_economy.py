import numpy as np
from tavern_ai.baseline import BaselinePolicy

def observation(*legal):
    m = np.zeros(245, dtype=bool)
    m[list(legal)] = True
    return {"action_mask": m}

def test_buy_precedes_positioning():
    assert BaselinePolicy().act(observation(0, 8, 126), {"turn": 1}) == 8

def test_forced_choice_overrides_action_guard():
    assert BaselinePolicy().act(observation(0, 30), {"actions_used": 99}) == 30

def test_position_once_economy_exhausted():
    policy = BaselinePolicy(max_actions_per_turn=16)
    assert policy.act(observation(0, 126), {"actions_used": 2}) == 126
    assert policy.act(observation(0, 126), {"actions_used": 16}) == 0

def test_play_precedes_buy():
    assert BaselinePolicy().act(observation(0, 8, 46), {"turn": 2}) == 46
