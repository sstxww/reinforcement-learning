"""Controlled, no-engine unit tests for the independent policy ablation."""
import numpy as np
import pytest

from tavern_ai.upgrade_priority_s_20261102_9c034841 import UpgradePriorityPolicy, POLICY


def obs(*actions):
    mask = np.zeros(245, dtype=bool)
    mask[list(actions)] = True
    return {"action_mask": mask, "features": np.zeros(4017), "cards": np.zeros(447)}


def test_planned_turn_prefers_legal_upgrade_to_buy():
    assert UpgradePriorityPolicy().act(obs(0, 3, 8), {"turn": 2, "actions_used": 0}) == 3


def test_off_schedule_preserves_baseline_buy_priority():
    assert UpgradePriorityPolicy().act(obs(0, 3, 8), {"turn": 4, "actions_used": 0}) == 8


def test_upgrade_only_when_legal():
    assert UpgradePriorityPolicy().act(obs(0, 8), {"turn": 5, "actions_used": 0}) == 8


def test_after_three_actions_returns_to_base_policy():
    assert UpgradePriorityPolicy().act(obs(0, 3, 8), {"turn": 5, "actions_used": 3}) == 8


@pytest.mark.parametrize("mask", [[], list(range(246))])
def test_mask_contract_fails_closed(mask):
    with pytest.raises(ValueError, match="245"):
        UpgradePriorityPolicy().act({"action_mask": np.ones(len(mask), dtype=bool)}, {"turn": 2})


def test_provenance_name_explicit():
    assert POLICY == "upgrade-priority-before-buy-v1"
