"""Pure unit tests. Fake masks are NOT real TavernGym match receipts."""
import numpy as np
import pytest

from tavern_ai.behavior_audit_v5_880b8a71 import category, decide


def test_action_semantics_spans():
    assert category(0) == "end_turn"
    assert category(3) == "upgrade"
    assert category(8) == category(15) == "buy"
    assert category(30) == "choose"
    assert category(46) == category(125) == "play"
    assert category(244) == "move"


def test_raw_action_preserved_without_guard():
    mask = np.zeros(245, dtype=bool)
    mask[[0, 8, 46]] = True
    assert decide(mask, 8, 100, None) == (8, False)
    assert decide(mask, 8, 35, 36) == (8, False)


def test_guard_uses_only_legal_end():
    mask = np.zeros(245, dtype=bool)
    mask[[0, 8]] = True
    assert decide(mask, 8, 36, 36) == (0, True)
    mask[0] = False
    assert decide(mask, 8, 100, 36) == (8, False)


def test_invalid_legal_mask_rejected():
    mask = np.zeros(245, dtype=bool)
    with pytest.raises(ValueError):
        decide(mask, 1, 0, None)
    mask[8] = True
    with pytest.raises(ValueError):
        decide(mask, 0, 0, None)
    with pytest.raises(ValueError):
        decide(mask, 245, 0, None)
