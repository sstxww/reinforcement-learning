"""Guard is a controlled changed-mask experiment, never mistaken for model-only."""
import numpy as np
import pytest

from tavern_ai.play_cancel_guard_902968f5 import guard_mask, update_cancel_blacklist


def mask(*ids):
    a = np.zeros(245, dtype=bool)
    for i in ids:
        a[i] = True
    return a


def test_cancel_after_play_adds_that_play_to_temporary_blocklist():
    b = set()
    assert update_cancel_blacklist(46, 7, b)
    assert b == {46}
    assert not update_cancel_blacklist(7, 46, b)


def test_mask_filters_previously_cancelled_play_but_preserves_native_buy():
    native = mask(0, 8, 46, 7)
    changed = guard_mask(native, {46})
    assert not changed[46]
    assert changed[8] and changed[7] and changed[0]
    assert not (changed & ~native).any()


def test_never_removes_sole_legal_action():
    native = mask(46)
    changed = guard_mask(native, {46})
    assert changed[46]


def test_no_cancel_supression_when_native_cancel_is_only_legal():
    native = mask(7)
    changed = guard_mask(native, {46})
    assert changed[7]


def test_invalid_mask_rejected():
    with pytest.raises(ValueError):
        guard_mask(np.zeros(245, dtype=bool), {46})


def test_unrelated_masks_unchanged():
    native = mask(0, 30, 126)
    assert (guard_mask(native, {46, 47}) == native).all()
