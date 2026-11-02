"""Action-opportunity diagnosis: no fabricated match results."""
import numpy as np
import pytest
from tavern_ai.contract import ACTIONS
from tavern_ai.opportunity_6b4eaf12 import opportunity


def test_ending_turn_while_buy_is_available():
    mask = np.zeros(ACTIONS, dtype=bool)
    mask[[0, 8, 46]] = True
    result = opportunity(mask, 0)
    assert result["buy_legal"] and result["play_legal"]
    assert result["end_selected"] and not result["buy_selected"]


def test_buy_choice_uses_true_mask():
    mask = np.zeros(ACTIONS, dtype=bool)
    mask[[0, 12]] = True
    result = opportunity(mask, 12)
    assert result["buy_legal"] and result["buy_selected"]
    assert not result["play_legal"]


def test_no_buy_opportunity_is_not_a_model_buy_miss():
    mask = np.zeros(ACTIONS, dtype=bool)
    mask[0] = True
    result = opportunity(mask, 0)
    assert not result["buy_legal"] and result["end_selected"]


def test_invalid_action_fails_closed():
    mask = np.zeros(ACTIONS, dtype=bool)
    mask[0] = True
    with pytest.raises(ValueError, match="legal"):
        opportunity(mask, 8)
