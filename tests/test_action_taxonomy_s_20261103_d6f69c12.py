"""Offline regression of the real, source-verified TavernGym action ID layout.

These are synthetic contract checks, NOT real matches or PPO strength evidence.
"""
import pytest

from tavern_ai.behavior_audit_v5_880b8a71 import category

@pytest.mark.parametrize("action, family", [
    (0, "end_turn"), (1, "refresh"), (2, "freeze"), (3, "upgrade"),
    (4, "hero_power"), (5, "hero_power"), (6, "dark_gift"),
    (7, "cancel"), (8, "buy"), (15, "buy"),
    (16, "sell"), (22, "sell"), (23, "activate"), (29, "activate"),
    (30, "choose"), (45, "choose"), (46, "play"), (125, "play"),
    (126, "magnetize"), (195, "magnetize"), (196, "move"), (244, "move"),
])
def test_every_pinned_action_family_boundary(action, family):
    assert category(action) == family

@pytest.mark.parametrize("invalid", [-1, 245, 999])
def test_invalid_action_ids_fail_closed(invalid):
    with pytest.raises(ValueError, match="out of bounds"):
        category(invalid)

def test_refresh_freeze_not_hidden_in_other():
    assert category(1) == "refresh"
    assert category(2) == "freeze"
    assert category(7) == "cancel"
