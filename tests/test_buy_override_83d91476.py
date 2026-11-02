import pytest
from tavern_ai.buy_override_83d91476 import BuyOpportunityOverride, summarise


class FakeModel:
    def __init__(self, action):
        self.action = action
    def predict(self, observation, *, action_masks, deterministic):
        return self.action, None


def mask(*actions):
    m = [False] * 245
    for action in actions:
        m[action] = True
    return m


@pytest.mark.parametrize("raw", [1, 2])
def test_override_replaces_only_refresh_freeze_when_buy_legal(raw):
    x = BuyOpportunityOverride(FakeModel(raw))
    actual, _ = x.predict({}, action_masks=mask(raw, 8, 12), deterministic=True)
    assert actual == 8 and x.counts["overrides"] == 1


def test_no_override_without_legal_buy():
    x = BuyOpportunityOverride(FakeModel(2))
    actual, _ = x.predict({}, action_masks=mask(2, 0), deterministic=True)
    assert actual == 2
    assert x.counts["overrides"] == 0


def test_preserves_native_buy_and_ends():
    for raw in (8, 0):
        x = BuyOpportunityOverride(FakeModel(raw))
        actual, _ = x.predict({}, action_masks=mask(0, 1, 8), deterministic=True)
        assert actual == raw and x.counts["overrides"] == 0


def test_rejects_illegal_action():
    with pytest.raises(ValueError, match="illegal"):
        BuyOpportunityOverride(FakeModel(8)).predict({}, action_masks=mask(0), deterministic=True)


def test_rejects_wrong_mask_shape():
    with pytest.raises(ValueError, match="width"):
        BuyOpportunityOverride(FakeModel(1)).predict({}, action_masks=[True], deterministic=True)


def test_cannot_summarize_no_games():
    with pytest.raises(ValueError, match="real paired"):
        summarise([])
