"""Unit checks for the isolated choice-position hypothesis."""
import numpy as np
import pytest

from tavern_ai.baseline import BaselinePolicy
from tavern_ai.discover_choice_experiment import LastChoicePolicy, summarize


def obs(*actions):
    mask = np.zeros(245, dtype=bool)
    mask[list(actions)] = True
    return {"action_mask": mask}


def test_baseline_and_candidate_diverge_only_on_multiple_choices():
    original = BaselinePolicy()
    candidate = LastChoicePolicy()
    state = obs(0, 30, 32, 35)
    assert original.act(state) == 30
    assert candidate.act(state) == 35


def test_single_choice_matches_baseline():
    state = obs(0, 33)
    assert LastChoicePolicy().act(state) == BaselinePolicy().act(state) == 33


@pytest.mark.parametrize("actions", [(0,), (0, 3), (0, 8), (0, 46), (0, 126)])
def test_no_choice_preserves_baseline(actions):
    state = obs(*actions)
    ctx = {"turn": 5, "actions_used": 1}
    assert LastChoicePolicy().act(state, ctx) == BaselinePolicy().act(state, ctx)


@pytest.mark.parametrize("mask", [np.zeros(245, dtype=bool), np.ones(244, dtype=bool)])
def test_invalid_masks_fail_closed(mask):
    with pytest.raises(ValueError):
        LastChoicePolicy().act({"action_mask": mask})


def test_recap_exposure_count_not_mistaken_for_improvement():
    x = [{"seed": 1, "placements": [8] + list(range(1, 8)),
          "choice_opportunities": 3, "candidate_choice_interventions": 0}]
    stats = summarize(x)
    assert stats["games"] == 1
    assert stats["mean_placement"] == 8
    assert stats["candidate_choice_interventions"] == 0
