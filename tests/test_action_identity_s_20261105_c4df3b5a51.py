"""Regression for raw discrete-action identity in TavernEnv.step.

These are synthetic input-boundary tests, NOT genuine eight-seat match receipts.
"""
from types import SimpleNamespace

import numpy as np
import pytest

from tavern_ai.action_identity import require_discrete_action
from tavern_ai.contract import ACTIONS
from tavern_ai.env import TavernEnv


@pytest.mark.parametrize("value", [0, 3, np.int32(3), np.int64(3), np.uint8(3)])
def test_true_discrete_integer_actions_remain_accepted(value):
    assert require_discrete_action(value) == int(value)


@pytest.mark.parametrize(
    "value",
    [True, False, 3.0, 3.9, float("nan"), np.float64(3.0),
     np.bool_(True), "3", None, np.array(3)],
)
def test_implicit_conversions_are_rejected(value):
    with pytest.raises(ValueError, match="integer scalar"):
        require_discrete_action(value)


def fake_env():
    env = object.__new__(TavernEnv)
    env._mask = np.zeros(ACTIONS, dtype=bool)
    env._mask[3] = True
    calls = []
    def game_step(action):
        calls.append(action)
        return {"test": "observation"}, 0.0, False, False, {}
    env.game = SimpleNamespace(step=game_step)
    env._map = lambda obs: obs
    return env, calls


def test_step_uses_exact_np_integer_selected_by_policy():
    env, calls = fake_env()
    result = env.step(np.int64(3))
    assert result[0] == {"test": "observation"}
    assert calls == [3]


@pytest.mark.parametrize("value", [True, 3.0, 3.9, "3", np.array(3)])
def test_step_fails_before_simulator_for_non_discrete_identity(value):
    env, calls = fake_env()
    with pytest.raises(ValueError, match="integer scalar"):
        env.step(value)
    assert calls == []


def test_integer_not_in_legal_mask_still_fails_closed():
    env, calls = fake_env()
    with pytest.raises(ValueError, match="Illegal action"):
        env.step(np.int64(4))
    assert calls == []
