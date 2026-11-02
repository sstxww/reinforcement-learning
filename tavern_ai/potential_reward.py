"""Experimental potential-based reward shaping for pinned TavernGym observe2.

Only used by this session's isolated experiment; never changes production training.
The first 42 features match upstream visible globals (health=5, tier=10, board=33).
F(s,a,s') = alpha * (gamma*Phi(s') - Phi(s)), with Phi(terminal)=0.
"""
from __future__ import annotations

import gymnasium as gym
import numpy as np

from .contract import ACTIONS

GAMMA = 0.99
HEALTH_INDEX, TIER_INDEX, BOARD_INDEX = 5, 10, 33


def potential(obs: dict) -> float:
    features = np.asarray(obs["features"], dtype=np.float32)
    if features.ndim != 1 or len(features) < 42:
        raise ValueError("Unexpected observe2 global feature layout")
    values = features[[HEALTH_INDEX, TIER_INDEX, BOARD_INDEX]]
    if not np.isfinite(values).all():
        raise ValueError("Non-finite potential features")
    health, tier, board = np.clip(values, 0.0, 1.0)
    return float(0.2 * health + 0.4 * tier + 0.4 * board)


def shaping_bonus(previous: float, following: float, *, alpha: float,
                  gamma: float = GAMMA, terminal: bool = False) -> float:
    if gamma <= 0 or gamma > 1 or alpha < 0:
        raise ValueError("Require 0 < gamma <= 1 and alpha >= 0")
    return float(alpha * (gamma * (0.0 if terminal else following) - previous))


class PotentialRewardWrapper(gym.Wrapper):
    """Exposes original action_masks to sb3-contrib and adds telescoping reward."""

    def __init__(self, env: gym.Env, *, alpha: float = 0.0,
                 gamma: float = GAMMA):
        super().__init__(env)
        if alpha < 0 or gamma <= 0 or gamma > 1:
            raise ValueError("Invalid shaping coefficients")
        self.alpha, self.gamma = float(alpha), float(gamma)
        self._previous: float | None = None
        self.steps = 0
        self.terminal_count = 0
        self.raw_reward_sum = 0.0
        self.bonus_sum = 0.0

    def action_masks(self):
        mask = np.asarray(self.env.action_masks(), dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise RuntimeError("Expected non-empty 245-action legal mask")
        return mask.copy()

    def reset(self, *, seed=None, options=None):
        obs, info = self.env.reset(seed=seed, options=options)
        self._previous = potential(obs)
        self.action_masks()
        return obs, info

    def step(self, action):
        if self._previous is None:
            raise RuntimeError("Call reset before step")
        if not self.action_masks()[int(action)]:
            raise ValueError("Illegal action passed to wrapper")
        obs, reward, terminated, truncated, info = self.env.step(action)
        terminal = bool(terminated or truncated)
        following = potential(obs)
        bonus = shaping_bonus(self._previous, following, alpha=self.alpha,
                              gamma=self.gamma, terminal=terminal)
        self._previous = 0.0 if terminal else following
        self.steps += 1
        self.terminal_count += int(terminal)
        self.raw_reward_sum += float(reward)
        self.bonus_sum += bonus
        return obs, float(reward) + bonus, terminated, truncated, info
