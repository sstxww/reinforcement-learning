"""Synthetic unit tests only. These are not game receipts."""
import numpy as np
import pytest

from tavern_ai.contract import ACTIONS
from tavern_ai.raw_sampling_probe_s406afe60 import choose_raw_action


class FakeModel:
    def __init__(self, selected):
        self.selected = selected
        self.flags = []

    def predict(self, obs, action_masks, deterministic):
        assert "features" in obs and "cards" in obs
        self.flags.append((deterministic, int(action_masks.sum())))
        return np.asarray(self.selected), None


def legal_mask():
    mask = np.zeros(ACTIONS, dtype=bool)
    mask[0] = True
    mask[9] = True
    return mask


@pytest.mark.parametrize("mode,deterministic", [("argmax", True), ("sampled", False)])
def test_selection_is_from_original_model(mode, deterministic):
    model = FakeModel(9)
    chosen = choose_raw_action(model, {"features": [], "cards": []}, legal_mask(), mode)
    assert chosen == 9
    assert model.flags == [(deterministic, 2)]


@pytest.mark.parametrize("illegal", [-1, 245, 8])
def test_invalid_raw_decision_rejected_without_rescue(illegal):
    with pytest.raises(ValueError, match="illegal"):
        choose_raw_action(FakeModel(illegal), {"features": [], "cards": []}, legal_mask(), "sampled")


def test_invalid_mode_and_mask_fail_closed():
    with pytest.raises(ValueError, match="mode"):
        choose_raw_action(FakeModel(9), {}, legal_mask(), "assisted")
    with pytest.raises(ValueError, match="mask"):
        choose_raw_action(FakeModel(0), {}, np.zeros(ACTIONS, dtype=bool), "argmax")
    with pytest.raises(ValueError, match="mask"):
        choose_raw_action(FakeModel(9), {}, np.ones(244, dtype=bool), "sampled")
