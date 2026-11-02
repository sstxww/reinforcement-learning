"""No engine dependency: check potential arithmetic and masked-action forwarding."""
import gymnasium as gym
import numpy as np
import pytest

from tavern_ai.contract import ACTIONS, CARDS, FEATURES
from tavern_ai.reward_shaping import PotentialRewardWrapper, observation_potential


def obs(health=1.0, tier=1.0 / 6, board=0.0):
    f = np.zeros(FEATURES, dtype=np.float32)
    f[5], f[10], f[32] = health, tier, board
    return {"features": f, "cards": np.zeros(CARDS, dtype=np.int32)}


class FakeEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = gym.spaces.Discrete(ACTIONS)
        self.observation_space = gym.spaces.Dict({
            "features": gym.spaces.Box(-np.inf, np.inf, shape=(FEATURES,)),
            "cards": gym.spaces.Box(0, 500, shape=(CARDS,), dtype=np.int32),
        })
        self.mask = np.zeros(ACTIONS, dtype=bool)
        self.mask[0] = True
        self.calls = 0

    def action_masks(self):
        return self.mask.copy()

    def reset(self, *, seed=None, options=None):
        self.calls = 0
        return obs(), {}

    def step(self, action):
        assert self.mask[action]
        self.calls += 1
        if self.calls == 1:
            return obs(health=0.8, tier=2 / 6, board=1 / 7), 0.0, False, False, {}
        return obs(health=0.0), 1.0, True, False, {}


def test_bounded_potential():
    assert 0 <= observation_potential(obs()) <= 0.32
    assert observation_potential(obs(tier=4 / 6)) > observation_potential(obs())
    bad = obs()
    bad["features"][5] = float("nan")
    with pytest.raises(ValueError):
        observation_potential(bad)


def test_mask_forwarding_and_telescope():
    env = PotentialRewardWrapper(FakeEnv(), gamma=0.99)
    first, _ = env.reset(seed=2)
    assert np.flatnonzero(env.action_masks()).tolist() == [0]
    initial = observation_potential(first)
    next_obs, reward, term, trunc, info = env.step(0)
    middle = observation_potential(next_obs)
    assert reward == pytest.approx(0.99 * middle - initial)
    assert not term and not trunc and info["raw_reward"] == 0
    _, terminal_reward, term, _, info = env.step(0)
    assert term and info["raw_reward"] == 1.0
    assert terminal_reward == pytest.approx(1.0 - middle)
    assert reward + 0.99 * terminal_reward == pytest.approx(0.99 - initial)


def test_control_arm_is_unmodified():
    env = PotentialRewardWrapper(FakeEnv(), strength=0.0)
    env.reset()
    _, r0, *_ = env.step(0)
    _, r1, *_ = env.step(0)
    assert r0 == 0.0 and r1 == 1.0


def test_reset_and_arguments():
    env = PotentialRewardWrapper(FakeEnv())
    with pytest.raises(RuntimeError):
        env.step(0)
    for kwargs in ({"gamma": 0}, {"strength": -1.0}):
        with pytest.raises(ValueError):
            PotentialRewardWrapper(FakeEnv(), **kwargs)
    env.reset()
    env.step(0)
    env.reset()
    assert env._previous_potential == pytest.approx(observation_potential(obs()))
