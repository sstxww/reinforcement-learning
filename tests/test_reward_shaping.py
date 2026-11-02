"""Reward ablation unit tests; do not need the TavernGym binary."""
import math
import pytest

from tavern_ai.reward import signed_log1p, SignedLogReward


@pytest.mark.parametrize("value", [0, 0.1, 1.0, 2.0, 10.0, 100.0])
def test_sign_and_order(value):
    pos = signed_log1p(value)
    neg = signed_log1p(-value)
    assert pos >= 0
    assert pos == pytest.approx(-neg, abs=1e-12)
    assert pos == pytest.approx(math.log1p(value))
    if value > 0:
        assert pos <= value


def test_order():
    values = [-100, -10, -1, 0, 1, 10, 100]
    assert list(map(signed_log1p, values)) == sorted(map(signed_log1p, values))


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_reject_nonfinite(value):
    with pytest.raises(ValueError, match="Non-finite"):
        signed_log1p(value)


def test_wrapper_inherits_gym_reward_wrapper():
    import gymnasium as gym
    assert issubclass(SignedLogReward, gym.RewardWrapper)
