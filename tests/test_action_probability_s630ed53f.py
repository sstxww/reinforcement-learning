"""Synthetic unit regressions for the raw action-distribution probe (NOT games)."""
import numpy as np
import pytest

from tavern_ai.action_probability_s630ed53f import family, summarize_probabilities
from tavern_ai.contract import ACTIONS


def empty_case():
    mask = np.zeros(ACTIONS, dtype=bool)
    probs = np.zeros(ACTIONS, dtype=np.float64)
    return mask, probs


def test_legal_buy_probability_is_not_equated_with_an_actual_buy():
    mask, p = empty_case()
    mask[[0, 1, 2, 8, 10]] = True
    p[[0, 1, 2, 8, 10]] = [0.01, 0.55, 0.34, 0.07, 0.03]
    s = summarize_probabilities(p, mask, action=1)
    assert s["buy_legal"] is True
    assert s["legal_buy_slots"] == 2
    assert s["legal_action_count"] == 5
    assert s["buy_probability"] == pytest.approx(0.10)
    assert s["best_buy_probability"] == pytest.approx(0.07)
    assert s["refresh_freeze_probability"] == pytest.approx(0.89)
    assert s["top_action_probability"] == pytest.approx(0.55)


def test_missing_buy_legal_is_not_a_missed_purchase():
    mask, p = empty_case()
    mask[[0, 1]] = True
    p[0] = 0.25
    p[1] = 0.75
    s = summarize_probabilities(p, mask, action=1)
    assert s["buy_legal"] is False
    assert s["legal_buy_slots"] == 0
    assert s["buy_probability"] == 0


@pytest.mark.parametrize("broken", ["masked", "sum", "nan", "negative", "illegal_choice", "shape"])
def test_invalid_policy_probabilities_fail_closed(broken):
    mask, p = empty_case()
    mask[[0, 1, 8]] = True
    p[[0, 1, 8]] = [0.1, 0.6, 0.3]
    chosen = 1
    if broken == "masked":
        p[16] = 0.01
        p[1] -= 0.01
    elif broken == "sum":
        p[1] = 0.5
    elif broken == "nan":
        p[1] = np.nan
    elif broken == "negative":
        p[16] = -0.02
        p[1] += 0.02
    elif broken == "illegal_choice":
        chosen = 16
    elif broken == "shape":
        mask = mask[:-1]
    with pytest.raises(ValueError):
        summarize_probabilities(p, mask, action=chosen)


def test_empty_legal_mask_fails():
    mask, p = empty_case()
    p[0] = 1.0
    with pytest.raises(ValueError):
        summarize_probabilities(p, mask, action=0)


@pytest.mark.parametrize("id_expected", [
    (0, "end_turn"), (1, "refresh"), (2, "freeze"), (7, "cancel"),
    (8, "buy"), (15, "buy"), (46, "play"), (125, "play"),
    (126, "magnetize"), (195, "magnetize"), (196, "move"), (244, "move"),
])
def test_pinned_action_family_boundaries(id_expected):
    ident, expected = id_expected
    assert family(ident) == expected


@pytest.mark.parametrize("bad", [-1, ACTIONS, 2.0, "8", None, True])
def test_out_of_range_action_rejected(bad):
    with pytest.raises(ValueError):
        family(bad)
