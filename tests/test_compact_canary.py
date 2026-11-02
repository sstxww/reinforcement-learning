"""Bounded-action intervention must respect the TavernGym legal mask."""
import numpy as np
import pytest
pytest.importorskip("sb3_contrib")
from tavern_ai.compact_canary import bounded_action, MAX_ACTIONS_PER_TURN


def test_guard_intervenes_only_with_legal_end_turn():
    mask = np.zeros(245, dtype=bool)
    mask[0] = True
    mask[3] = True
    assert bounded_action(3, mask, MAX_ACTIONS_PER_TURN - 1) == (3, False)
    assert bounded_action(3, mask, MAX_ACTIONS_PER_TURN) == (0, True)


def test_guard_never_invents_an_illegal_action():
    mask = np.zeros(245, dtype=bool)
    mask[3] = True
    assert bounded_action(3, mask, MAX_ACTIONS_PER_TURN) == (3, False)
    with pytest.raises(ValueError, match="Illegal"):
        bounded_action(4, mask, 0)
    with pytest.raises(ValueError, match="empty"):
        bounded_action(3, np.zeros(245, dtype=bool), 0)
