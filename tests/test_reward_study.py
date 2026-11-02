"""Unit tests independent from TavernGym installation."""
import gymnasium as gym
import numpy as np
import pytest

from tavern_ai.reward_study import RewardScale


class DummyEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Discrete(2)
        self.mask = np.array([True, False, True])

    def action_masks(self):
        return self.mask.copy()

    def reset(self, *, seed=None, options=None):
        return 0, {}

    def step(self, action):
        return 1, 2.0, False, False, {"source": "dummy"}


def test_reward_scale_preserves_mask_and_termination():
    env = RewardScale(DummyEnv(), 0.25)
    obs, reward, terminated, truncated, info = env.step(0)
    assert (obs, reward, terminated, truncated) == (1, 0.5, False, False)
    assert info == {"source": "dummy"}
    assert np.array_equal(env.action_masks(), [True, False, True])
    assert env.action_masks() is not env.env.mask


def test_raw_control_is_identity():
    env = RewardScale(DummyEnv(), 1.0)
    assert env.step(0)[1] == 2.0


@pytest.mark.parametrize("scale", [0.0, -1.0, float("nan"), float("inf")])
def test_reject_invalid_scale(scale):
    with pytest.raises(ValueError):
        RewardScale(DummyEnv(), scale)


def test_timesteps_validation_before_engine_import(tmp_path):
    from tavern_ai.reward_study import train_arm
    with pytest.raises(ValueError, match="divisible"):
        train_arm(seed=12, steps=130, scale=1.0,
                  out=tmp_path / "m.zip", metrics=tmp_path / "m.json")
