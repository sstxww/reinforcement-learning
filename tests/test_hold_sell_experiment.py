"""Unit tests for this session's optional optional magnetize-suppression policy."""
import numpy as np
import pytest

from tavern_ai.baseline import BaselinePolicy
from tavern_ai.hold_sell_experiment import AvoidMagnetizePolicy, SELL_ACTIONS, MAGNETIZE_ACTIONS, summarize


def obs(*actions):
    mask = np.zeros(245, dtype=bool)
    mask[list(actions)] = True
    return {"action_mask": mask}


def test_isolated_strategy_changes_magnetize_before_buy():
    state = obs(0, 8, 126)
    assert BaselinePolicy().act(state, {"turn": 3}) == 126
    assert AvoidMagnetizePolicy().act(state, {"turn": 3}) == 8


def test_avoid_magnetize_ends_instead_of_magnetizing():
    assert AvoidMagnetizePolicy().act(obs(0, 126), {"turn": 3}) == 0


def test_mandatory_action_not_skipped():
    assert AvoidMagnetizePolicy().act(obs(0, 30, 126), {"actions_used": 70}) == 30


def test_play_and_upgrade_schedule_preserved():
    policy = AvoidMagnetizePolicy()
    assert policy.act(obs(0, 3, 8, 46), {"turn": 2}) == 46
    assert policy.act(obs(0, 3, 8), {"turn": 2}) == 3
    assert policy.act(obs(0, 3, 8), {"turn": 3}) == 8


def test_per_turn_safety_end():
    assert AvoidMagnetizePolicy().act(obs(0, 8), {"actions_used": 86}) == 0
    assert AvoidMagnetizePolicy().act(obs(0, 8), {"actions_used": 61}) == 8


def test_forced_fallback_remains_legal():
    assert AvoidMagnetizePolicy().act(obs(126)) == 126


def test_invalid_mask_fails_closed():
    with pytest.raises(ValueError):
        AvoidMagnetizePolicy().act(obs())
    with pytest.raises(ValueError):
        AvoidMagnetizePolicy().act({"action_mask": np.ones(244, dtype=bool)})


def test_metrics_are_numeric_and_labelled():
    fake = [{"placements": [8], "seed": 1}, {"placements": [2], "seed": 2}]
    out = summarize(fake)
    assert out["games"] == 2
    assert out["mean_placement"] == 5
    assert out["first_place_rate"] == 0
    assert out["top4_rate"] == 0.5

def test_action_layout_regression_from_pinned_upstream():
    # Verified against MCG-NJU/AutoTavern actions.rs @ fb61201.
    assert tuple(SELL_ACTIONS) == tuple(range(16, 23))
    assert tuple(MAGNETIZE_ACTIONS) == tuple(range(126, 196))
    assert 126 not in SELL_ACTIONS
    assert 16 not in MAGNETIZE_ACTIONS

def test_non_magnetize_fallback_upgrade_matches_baseline():
    state = obs(0, 3)
    context = {"turn": 3, "actions_used": 1}
    assert BaselinePolicy().act(state, context) == 3
    assert AvoidMagnetizePolicy().act(state, context) == 3


def test_only_magnetize_priority_differs_on_representative_masks():
    policy = AvoidMagnetizePolicy()
    control = BaselinePolicy()
    for actions, turn, used in [
        ((0,), 3, 0),
        ((0, 8, 3), 3, 0),
        ((0, 8, 46, 126), 3, 0),
        ((0, 30, 126), 2, 95),
        ((0, 126), 3, 0),
        ((0, 1, 3), 3, 0),
        ((0, 8), 2, 86),
    ]:
        state = obs(*actions)
        ctxt = {"turn": turn, "actions_used": used}
        lhs, rhs = policy.act(state, ctxt), control.act(state, ctxt)
        assert lhs == rhs or rhs in MAGNETIZE_ACTIONS
