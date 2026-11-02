"""Isolated placement-only parameter tests (no engine dependency)."""
import numpy as np
from tavern_ai.baseline import BaselinePolicy
from tavern_ai.placement_probe import RightmostPlayPolicy

def obs(*legal):
    mask = np.zeros(245, dtype=bool)
    mask[list(legal)] = True
    return {"action_mask": mask}

def test_rightmost_first_hand():
    o = obs(0,46,47,48,54,55)
    assert BaselinePolicy().act(o) == 46
    assert RightmostPlayPolicy().act(o) == 48

def test_other_hand_stays_same_hand():
    o = obs(0,54,55,61,62)
    assert RightmostPlayPolicy().act(o) == 61

def test_mandatory_choice_unchanged():
    assert RightmostPlayPolicy().act(obs(0,30,46,53)) == 30

def test_all_other_nonplay_actions_unchanged():
    for legal in [(0,9),(0,3),(0,126),(0,196),(0,)]:
        o=obs(*legal)
        assert RightmostPlayPolicy().act(o) == BaselinePolicy().act(o)

def test_rightmost_legal_must_not_leave_hand_group():
    assert RightmostPlayPolicy().act(obs(0,47,53,55,62)) == 53
