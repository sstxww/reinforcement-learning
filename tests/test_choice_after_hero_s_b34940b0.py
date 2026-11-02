import numpy as np
import pytest
from tavern_ai.baseline import BaselinePolicy
from tavern_ai.choice_after_hero_s_b34940b0 import (
    FullLastPolicy, PostHeroLastPolicy, play, experiment
)

def obs(*xs):
    m = np.zeros(245, dtype=bool)
    m[list(xs)] = True
    return {"action_mask": m}

def test_original_and_all_last_choose():
    x = obs(0, 30, 32, 39)
    assert BaselinePolicy().act(x, {"turn": 0}) == 30
    assert FullLastPolicy().act(x, {"turn": 0}) == 39

def test_preserve_hero_selection_only():
    x = obs(0, 30, 32, 39)
    p = PostHeroLastPolicy()
    assert p.act(x, {"turn": 0}) == 30
    assert p.act(x, {"turn": 1}) == 39
    assert p.act(x, {"turn": 10}) == 39

def test_nondiscovery_unchanged():
    p = PostHeroLastPolicy()
    for x in (obs(0, 9), obs(0, 46, 9), obs(0)):
        assert p.act(x, {"turn": 5}) == BaselinePolicy().act(x, {"turn": 5})

def test_strict_mask_contract():
    with pytest.raises(ValueError):
        PostHeroLastPolicy().act(obs(), {"turn": 2})
    with pytest.raises(ValueError):
        FullLastPolicy().act({"action_mask": np.ones(3, dtype=bool)}, {"turn": 1})

def test_policy_names_and_budget(tmp_path):
    with pytest.raises(ValueError, match="Unknown"):
        play(1, "fake")
    with pytest.raises(ValueError, match="distinct"):
        experiment([1,1], tmp_path / "r", tmp_path / "metrics.json")
