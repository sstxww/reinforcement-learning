import numpy as np
import pytest
from tavern_ai.reward_eval import choose_action


class FakeModel:
    def predict(self, observation, *, action_masks, deterministic):
        assert deterministic
        assert action_masks[3]
        return 3, None


def test_capped_policy_ends_turn_legally():
    mask = np.zeros(245, dtype=bool)
    mask[[0, 3]] = True
    assert choose_action(FakeModel(), {}, mask, 18, 18) == (0, True)
    assert choose_action(FakeModel(), {}, mask, 17, 18) == (3, False)


def test_mandatory_choices_do_not_get_overridden():
    mask = np.zeros(245, dtype=bool)
    mask[3] = True
    assert choose_action(FakeModel(), {}, mask, 20, 18) == (3, False)


@pytest.mark.parametrize("mask", [np.zeros(245, dtype=bool), np.ones(200, dtype=bool)])
def test_reject_invalid_masks(mask):
    with pytest.raises(ValueError):
        choose_action(FakeModel(), {}, mask, 0, 18)
