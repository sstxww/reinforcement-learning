"""Pin raw TavernGym action-family semantics for rank-eight diagnostics.

This is offline synthetic regression only. It does not simulate or claim games.
"""
import pytest

from tavern_ai.buy_opportunity_68099929 import classify, summary_from_decisions


@pytest.mark.parametrize(
    ("action", "family"),
    [(0, "end_turn"), (1, "reroll"), (2, "freeze"), (3, "upgrade"),
     (8, "buy"), (15, "buy"), (16, "sell"), (30, "choose"), (46, "play")],
)
def test_pinned_action_family(action, family):
    assert classify(action) == family


def test_buy_opportunity_report_distinguishes_freeze_from_undifferentiated_other():
    events = [
        {"turn": 1, "action": 2, "buy_legal": True, "state_hash": "s1",
         "same_public_state_as_prior": False},
        {"turn": 1, "action": 2, "buy_legal": True, "state_hash": "s2",
         "same_public_state_as_prior": False},
        {"turn": 1, "action": 1, "buy_legal": True, "state_hash": "s3",
         "same_public_state_as_prior": False},
        {"turn": 2, "action": 8, "buy_legal": True, "state_hash": "s4",
         "same_public_state_as_prior": False},
    ]
    result = summary_from_decisions(events)
    assert result["buy_legal_decisions"] == 4
    assert result["buy_chosen"] == 1
    assert result["by_action_family"]["freeze"] == 2
    assert result["by_action_family"]["reroll"] == 1
    assert result["by_action_family"]["buy"] == 1
    assert result["by_action_family"].get("other", 0) == 0
