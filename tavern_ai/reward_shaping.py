"""Optional potential-based reward shaping using *public* observe2 fields.

The underlying TavernGym reward remains the source of truth.  This wrapper is
opt-in and is not wired into the shared V1 training workflow.
"""
from __future__ import annotations

import gymnasium as gym
import numpy as np

from .contract import FEATURES


def observation_potential(observation: dict) -> float:
    """Bounded potential from pinned observe2: own health, armor, tier, board count.

    Field offsets come from upstream crates/taverngym/src/obs.rs global features:
    health=5 (/40), armor=6 (/20), tavern tier=10 (/6), board count=32 (/7).
    Never reads opponent private state or raw game state.
    """
    features = np.asarray(observation["features"], dtype=np.float32)
    if features.shape != (FEATURES,) or not np.isfinite(features).all():
        raise ValueError("Invalid public observe2 features")
    health = float(np.clip(features[5], 0.0, 1.0))
    armor = float(np.clip(features[6], 0.0, 1.0))
    tier = float(np.clip(features[10], 0.0, 1.0))
    board = float(np.clip(features[32], 0.0, 1.0))
    return 0.04 * health + 0.02 * armor + 0.18 * tier + 0.08 * board


class PotentialRewardWrapper(gym.Wrapper):
    """Apply R' = R + strength*(gamma*Phi(s') - Phi(s)).

    Phi(terminal)=0, so discounted shaping telescopes to a policy-independent
    constant for an episode starting at a fixed observation. gamma must agree
    with the learner's discount. strength=0 is an exact control arm.
    """

    def __init__(self, env: gym.Env, gamma: float = 0.99, strength: float = 1.0):
        super().__init__(env)
        if not 0 < gamma <= 1 or not np.isfinite(gamma):
            raise ValueError("gamma must be finite and within (0, 1]")
        if strength < 0 or not np.isfinite(strength):
            raise ValueError("strength must be finite and nonnegative")
        self.gamma = float(gamma)
        self.strength = float(strength)
        self._previous_potential: float | None = None

    def action_masks(self):
        """Explicitly preserve MaskablePPO's legal-action interface."""
        return self.env.action_masks()

    def reset(self, *, seed=None, options=None):
        obs, info = self.env.reset(seed=seed, options=options)
        self._previous_potential = observation_potential(obs)
        return obs, info

    def step(self, action):
        if self._previous_potential is None:
            raise RuntimeError("Call reset before step")
        obs, reward, terminated, truncated, info = self.env.step(action)
        next_potential = 0.0 if terminated or truncated else observation_potential(obs)
        bonus = self.strength * (
            self.gamma * next_potential - self._previous_potential
        )
        self._previous_potential = next_potential
        return obs, float(reward) + bonus, terminated, truncated, {
            **info, "raw_reward": float(reward), "shaping_bonus": float(bonus)
        }
