"""Synthetic tests isolate reward algebra and mask delegation; engine tested in Actions."""
import numpy as np
import pytest
import gymnasium as gym
from gymnasium import spaces

from tavern_ai.potential_reward import (
    GAMMA, PotentialRewardWrapper, potential, shaping_bonus,
)


def obs(health=1.0, tier=0.2, board=0.0):
    f = np.zeros(4017, dtype=np.float32)
    f[5], f[10], f[33] = health, tier, board
    return {"features": f, "cards": np.zeros(447, dtype=np.int32)}


class FakeEnv(gym.Env):
    action_space = spaces.Discrete(245)
    observation_space = spaces.Dict({
        "features": spaces.Box(-np.inf, np.inf, shape=(4017,), dtype=np.float32),
        "cards": spaces.Box(0, 999, shape=(447,), dtype=np.int32),
    })
    def __init__(self):
        self.stage = 0

    def action_masks(self):
        m = np.zeros(245, dtype=bool)
        m[0] = True
        return m

    def reset(self, *, seed=None, options=None):
        self.stage = 0
        return obs(), {}

    def step(self, action):
        self.stage += 1
        return obs(board=0.5), 1.0, True, False, {}


def test_observation_potential():
    assert potential(obs(health=1, tier=1, board=1)) == pytest.approx(1.0)
    assert potential(obs(health=-1, tier=2, board=0)) == pytest.approx(0.4)
    with pytest.raises(ValueError):
        potential({"features": [1, 2]})


def test_discounted_telescope():
    p0, p1, p2 = 0.2, 0.7, 0.9
    first = shaping_bonus(p0, p1, alpha=0.5, gamma=GAMMA)
    last = shaping_bonus(p1, p2, alpha=0.5, gamma=GAMMA, terminal=True)
    assert first + GAMMA * last == pytest.approx(-0.5 * p0)


def test_terminal_and_control():
    baseline = PotentialRewardWrapper(FakeEnv(), alpha=0.0)
    shaped = PotentialRewardWrapper(FakeEnv(), alpha=0.5)
    baseline.reset(seed=8)
    shaped.reset(seed=8)
    assert baseline.action_masks().sum() == 1
    assert baseline.step(0)[1] == pytest.approx(1.0)
    shaped_reward = shaped.step(0)[1]
    assert shaped_reward == pytest.approx(1.0 - 0.5 * potential(obs()))
    assert shaped.terminal_count == 1
    with pytest.raises(ValueError):
        baseline.step(1)
