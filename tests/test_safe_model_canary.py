"""Mask and termination guard tests (do not require engine installation)."""
import numpy as np
import pytest
from tavern_ai.safe_model_canary import choose_action


class Stub:
    def __init__(self, action):
        self.action = action
        self.calls = 0
    def predict(self, obs, action_masks, deterministic):
        self.calls += 1
        assert deterministic is True
        return np.array(self.action), None


def test_model_chooses_action_before_cap():
    model = Stub(14)
    mask = np.zeros(245, dtype=bool)
    mask[[0, 14]] = True
    assert choose_action(model, {}, mask, used=2, cap=64) == (14, False)
    assert model.calls == 1


def test_guard_forces_only_legal_end_turn():
    model = Stub(14)
    mask = np.zeros(245, dtype=bool)
    mask[[0, 14]] = True
    assert choose_action(model, {}, mask, used=64, cap=64) == (0, True)
    assert model.calls == 0
    mask[0] = False
    assert choose_action(model, {}, mask, used=64, cap=64) == (14, False)


def test_never_accepts_illegal_model_actions():
    model = Stub(15)
    mask = np.zeros(245, dtype=bool)
    mask[[0, 14]] = True
    with pytest.raises(ValueError, match="Illegal masked"):
        choose_action(model, {}, mask, used=0)


def test_rejects_empty_mask():
    with pytest.raises(ValueError):
        choose_action(Stub(0), {}, np.zeros(245, dtype=bool), used=0)
