"""Regression tests for the session-only action-priority ablation."""
import numpy as np
import pytest

from tavern_ai.purchase_before_play_s64405d5e import PurchaseBeforePlay


def obs(*actions):
    mask = np.zeros(245, dtype=bool)
    for a in actions:
        mask[a] = True
    return {"action_mask": mask}


def test_purchase_precedes_legal_play_only_in_target_state():
    action, intervened = PurchaseBeforePlay().act(
        obs(0, 8, 9, 46, 51), {"turn": 3, "actions_used": 2}
    )
    assert (action, intervened) == (8, True)


def test_preserve_play_if_cannot_afford_buy():
    assert PurchaseBeforePlay().act(
        obs(0, 46, 126), {"turn": 3, "actions_used": 4}
    ) == (46, False)


def test_pending_choose_has_unconditional_priority():
    assert PurchaseBeforePlay().act(
        obs(0, 8, 30, 46), {"turn": 3, "actions_used": 2}
    ) == (30, False)


def test_turn_safety_cap_and_end_action_unchanged():
    assert PurchaseBeforePlay().act(
        obs(0, 8, 46), {"turn": 3, "actions_used": 85}
    ) == (0, False)


def test_does_not_intervene_on_magnetize_action():
    assert PurchaseBeforePlay().act(
        obs(0, 8, 126), {"turn": 3, "actions_used": 2}
    ) == (126, False)


def test_reject_invalid_mask_before_override():
    with pytest.raises(ValueError, match="245-action"):
        PurchaseBeforePlay().act({"action_mask": [True]})
