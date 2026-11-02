"""Session-isolated regression tests for opening Tavern upgrade scheduling."""
import numpy as np
import pytest

from tavern_ai.baseline import BaselinePolicy
from tavern_ai.s_20261102_509af6d2 import DelayedOpeningUpgradePolicy, summarize


def observation(*legal):
    mask = np.zeros(245, dtype=bool)
    mask[list(legal)] = True
    return {"action_mask": mask}


def test_original_turn_two_upgrade_remains_unchanged():
    assert BaselinePolicy().act(observation(0, 3, 8), {"turn": 2}) == 3


def test_candidate_turn_two_buys_instead_of_upgrading():
    policy = DelayedOpeningUpgradePolicy()
    assert policy.act(observation(0, 3, 8), {"turn": 2}) == 8


def test_candidate_turn_two_ends_instead_of_upgrading_without_buy():
    assert DelayedOpeningUpgradePolicy().act(observation(0, 3), {"turn": 2}) == 0


def test_candidate_upgrades_on_turn_three_before_buy():
    assert DelayedOpeningUpgradePolicy().act(observation(0, 3, 8), {"turn": 3}) == 3


def test_mandatory_choice_precedes_upgrade():
    policy = DelayedOpeningUpgradePolicy()
    assert policy.act(observation(0, 3, 30), {"turn": 2}) == 30
    assert policy.act(observation(0, 3, 30), {"turn": 3}) == 30


def test_play_precedes_upgrade():
    policy = DelayedOpeningUpgradePolicy()
    assert policy.act(observation(0, 3, 46), {"turn": 2}) == 46
    assert policy.act(observation(0, 3, 46), {"turn": 3}) == 46


def test_only_legal_upgrade_not_masked():
    assert DelayedOpeningUpgradePolicy().act(observation(3), {"turn": 2}) == 3


def test_action_budget_still_ends_turn():
    assert DelayedOpeningUpgradePolicy().act(
        observation(0, 3, 8), {"turn": 3, "actions_used": 85}
    ) == 0


def test_invalid_masks_fail_closed():
    policy = DelayedOpeningUpgradePolicy()
    with pytest.raises(ValueError, match="mask"):
        policy.act(observation(), {"turn": 2})
    with pytest.raises(ValueError, match="mask"):
        policy.act({"action_mask": np.ones(244, dtype=bool)}, {"turn": 2})


def test_descriptive_summary_does_not_invent_metrics():
    receipts = [
        {"seed": 1, "placements": [8, 1, 2, 3, 4, 5, 6, 7]},
        {"seed": 2, "placements": [3, 1, 2, 4, 5, 6, 7, 8]},
    ]
    assert summarize(receipts) == {
        "games": 2,
        "seeds": [1, 2],
        "placements": [8, 3],
        "mean_rank": 5.5,
        "first_place_rate": 0,
        "top_four_rate": 0.5,
    }
