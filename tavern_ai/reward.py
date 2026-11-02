"""Optional, monotone terminal-reward compression for controlled PPO ablations.

This module leaves the original TavernGym observations and rewards untouched
unless an experiment explicitly wraps the environment.
"""
from __future__ import annotations

import math
import gymnasium as gym


def signed_log1p(value: float) -> float:
    """Preserve sign/order/zero while reducing large reward magnitudes."""
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Non-finite environment reward")
    return math.copysign(math.log1p(abs(value)), value) if value else 0.0


class SignedLogReward(gym.RewardWrapper):
    """Applies signed_log1p to rewards; action masks remain on the base env."""

    def reward(self, reward: float) -> float:
        return signed_log1p(reward)
