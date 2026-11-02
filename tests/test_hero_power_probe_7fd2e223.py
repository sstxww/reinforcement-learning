"""Legality and guard regressions for isolated end-turn hero-power experiment."""
import numpy as np
import pytest
from tavern_ai.hero_power_probe_7fd2e223 import IdleHeroPowerPolicy, summarize


def obs(*actions):
    mask = np.zeros(245, dtype=bool)
    mask[list(actions)] = True
    return {"action_mask": mask}


def test_only_when_original_policy_ends_turn():
    p = IdleHeroPowerPolicy()
    assert p.act(obs(0, 8, 4), {"turn": 1, "actions_used": 1}) == 8
    assert p.act(obs(0, 3, 5), {"turn": 2, "actions_used": 1}) == 3
    assert p.hero_power_uses == 0


def test_first_legal_hero_power_only_once_per_turn():
    p = IdleHeroPowerPolicy()
    assert p.act(obs(0, 5), {"turn": 2, "actions_used": 1}) == 5
    assert p.act(obs(0, 5), {"turn": 2, "actions_used": 2}) == 0
    assert p.act(obs(0, 4, 5), {"turn": 3, "actions_used": 1}) == 4
    assert p.hero_power_uses == 2


def test_never_override_safety_cap_or_unavailable_power():
    p = IdleHeroPowerPolicy()
    assert p.act(obs(0, 4), {"turn": 1, "actions_used": 60}) == 0
    assert p.act(obs(0), {"turn": 1, "actions_used": 2}) == 0
    assert p.hero_power_uses == 0


def test_invalid_mask_fails_closed():
    p = IdleHeroPowerPolicy()
    with pytest.raises(ValueError):
        p.act(obs(), {"turn": 1})


def test_summary_uses_observed_records_only():
    data = [
        {"placements": [2,1,3,4,5,6,7,8], "seed": 9, "hero_power_uses": 3},
        {"placements": [7,1,2,3,4,5,6,8], "seed": 10, "hero_power_uses": 4},
    ]
    x = summarize(data)
    assert x == {
        "games": 2, "mean_placement": 4.5, "top4_rate": 0.5,
        "first_place_rate": 0, "placements": [2, 7], "seeds": [9, 10],
        "total_hero_power_uses": 7,
    }
