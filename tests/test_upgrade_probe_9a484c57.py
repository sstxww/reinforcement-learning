"""Fast isolated action-mask and policy tests (no synthetic match claims)."""
import numpy as np
import pytest
from tavern_ai.upgrade_probe_9a484c57 import ACTION_BUDGET, select_action


def obs(*legal):
    mask = np.zeros(245, dtype=bool)
    mask[list(legal)] = True
    return {"action_mask": mask}


def test_prioritize_scheduled_upgrade_over_buy():
    assert select_action(obs(0, 3, 8), {"turn": 2, "actions_used": 0}, True) == 3


def test_never_override_mandatory_discovery():
    assert select_action(obs(0, 3, 8, 31), {"turn": 2}, True) == 31


def test_not_upgrade_twice():
    assert select_action(obs(0, 3, 8), {"turn": 2, "upgraded_this_turn": True}, True) == 8


def test_unscheduled_turn_and_control_match_baseline():
    ctx = {"turn": 3}
    assert select_action(obs(0, 3, 8), ctx, True) == 8
    assert select_action(obs(0, 3, 8), {"turn": 2}, False) == 8


def test_end_turn_budget_same_for_both_arms():
    for arm in (True, False):
        assert select_action(obs(0, 3, 8), {"turn": 2, "actions_used": ACTION_BUDGET}, arm) == 0


def test_end_turn_if_only_legal():
    assert select_action(obs(0), {"turn": 2}, True) == 0


def test_all_returned_actions_are_legal():
    rng = np.random.default_rng(9)
    for _ in range(200):
        actions = rng.choice(np.arange(245), size=int(rng.integers(1, 20)), replace=False)
        observation = obs(*actions)
        for arm in (False, True):
            action = select_action(observation, {"turn": 5, "actions_used": 0}, arm)
            assert observation["action_mask"][action]


def test_reject_empty_mask():
    with pytest.raises(ValueError):
        select_action(obs(), {"turn": 2}, True)
