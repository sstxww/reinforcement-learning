"""Unit-only fixtures do not represent actual games."""
import numpy as np
import pytest

from tavern_ai.buy_priority_s_90e24c7b import MaskLegalBuyOverride


class FakeModel:
    def __init__(self, action):
        self.action = action
        self.calls = 0

    def predict(self, obs, action_masks, deterministic=True):
        self.calls += 1
        assert deterministic
        return np.asarray(self.action), None


def test_buy_override_when_buy_mask_legal():
    mask = np.zeros(245, dtype=bool)
    mask[[0, 7, 8, 12]] = True
    fake = FakeModel(7)
    wrapper = MaskLegalBuyOverride(fake)
    action, state = wrapper.predict({"features": np.zeros(4017)}, mask)
    assert int(action) == 8 and state is None
    assert wrapper.overrides == 1
    assert wrapper.model_wanted_nonbuy_while_buy_legal == 1
    assert fake.calls == 1


def test_no_override_if_buy_is_not_mask_legal():
    mask = np.zeros(245, dtype=bool)
    mask[[0, 7]] = True
    wrapper = MaskLegalBuyOverride(FakeModel(7))
    action, _ = wrapper.predict({}, mask)
    assert int(action) == 7
    assert wrapper.overrides == 0


def test_no_override_if_model_already_buys():
    mask = np.zeros(245, dtype=bool)
    mask[[0, 8, 9]] = True
    wrapper = MaskLegalBuyOverride(FakeModel(9))
    action, _ = wrapper.predict({}, mask)
    assert int(action) == 9
    assert wrapper.model_wanted_buy == 1
    assert wrapper.overrides == 0


def test_reject_underlying_illegal_action():
    mask = np.zeros(245, dtype=bool)
    mask[8] = True
    with pytest.raises(ValueError, match="illegal"):
        MaskLegalBuyOverride(FakeModel(7)).predict({}, mask)


def test_reject_wrong_mask_shape():
    with pytest.raises(ValueError, match="245"):
        MaskLegalBuyOverride(FakeModel(0)).predict({}, np.ones(244, dtype=bool))
