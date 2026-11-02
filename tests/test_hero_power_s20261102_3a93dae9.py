"""Offline regressions for session-local affordable hero-power ablation."""
import numpy as np
import pytest

from tavern_ai.hero_power_ablation_s20261102_3a93dae9 import AffordableHeroPowerPolicy


def observation(*, free=True, second=False, pending=False):
    features = np.zeros(4017, dtype=np.float32)
    features[17] = 0 if free else 0.8  # pinned observe2: hero power price / 5
    features[20] = 0
    features[7] = 0.8  # 8 gold, preserve at least 3 after power
    mask = np.zeros(245, dtype=bool)
    mask[[0, 4, 8]] = True
    if second:
        mask[5] = True
    if pending:
        mask[:] = False
        mask[30] = True
    return {"features": features, "cards": np.zeros(447, dtype=np.int32), "action_mask": mask}


def test_affordable_hero_power_at_most_once_per_turn():
    p = AffordableHeroPowerPolicy()
    obs = observation()
    assert p.act(obs, {"turn": 3, "actions_used": 0}) == 4
    assert p.act(obs, {"turn": 3, "actions_used": 1}) == 8
    assert p.act(obs, {"turn": 4, "actions_used": 0}) == 4
    assert p.hero_actions == 2


def test_expensive_power_does_not_override_baseline_buy():
    p = AffordableHeroPowerPolicy()
    assert p.act(observation(free=False), {"turn": 3, "actions_used": 0}) == 8
    assert p.hero_actions == 0


def test_second_slot_when_first_costs_gold():
    p = AffordableHeroPowerPolicy()
    assert p.act(observation(free=False, second=True), {"turn": 4, "actions_used": 0}) == 5


def test_outstanding_choice_takes_precedence():
    p = AffordableHeroPowerPolicy()
    assert p.act(observation(pending=True), {"turn": 5, "actions_used": 0}) == 30
    assert p.hero_actions == 0


def test_invalid_empty_mask_fails_closed():
    p = AffordableHeroPowerPolicy()
    obs = observation()
    obs["action_mask"][:] = False
    with pytest.raises(ValueError, match="nonempty"):
        p.act(obs, {"turn": 1})


def test_bad_feature_shape_fails_closed():
    p = AffordableHeroPowerPolicy()
    obs = observation()
    obs["features"] = np.zeros(5, dtype=np.float32)
    with pytest.raises(ValueError, match="feature layout"):
        p.act(obs, {"turn": 1})
