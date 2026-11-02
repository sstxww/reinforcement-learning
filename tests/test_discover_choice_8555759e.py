"""Unit tests for the isolated choice tie-break; no mocked game results."""
import numpy as np
import pytest

from tavern_ai.baseline import BaselinePolicy
from tavern_ai.experiment_s_20261102_8555759e import LastChoicePolicy, choice_candidates


def observed_mask(*actions):
    mask = np.zeros(245, dtype=bool)
    mask[list(actions)] = True
    return {"action_mask": mask}


def test_changes_only_choice_tie_break():
    obs = observed_mask(0, 8, 30, 33, 45)
    assert BaselinePolicy().act(obs) == 30
    assert LastChoicePolicy().act(obs) == 45
    assert choice_candidates(obs["action_mask"]).tolist() == [30, 33, 45]


@pytest.mark.parametrize(
    "actions,context",
    [
        ((0, 8, 46), {"turn": 2, "actions_used": 0}),
        ((0, 8, 9), {"turn": 2, "actions_used": 0}),
        ((0, 3, 8), {"turn": 2, "actions_used": 0}),
        ((0, 8), {"turn": 3, "actions_used": 86}),
        ((0,), {"turn": 1, "actions_used": 0}),
    ],
)
def test_delegates_non_choice_actions_to_original_baseline(actions, context):
    obs = observed_mask(*actions)
    assert LastChoicePolicy().act(obs, context) == BaselinePolicy().act(obs, context)


def test_single_mandatory_choice_is_identical():
    obs = observed_mask(0, 34)
    assert LastChoicePolicy().act(obs) == BaselinePolicy().act(obs) == 34


def test_rejects_wrong_mask_or_empty_legal_mask():
    policy = LastChoicePolicy()
    with pytest.raises(ValueError):
        policy.act({"action_mask": np.zeros(245, dtype=bool)})
    with pytest.raises(ValueError):
        policy.act({"action_mask": np.ones(244, dtype=bool)})
