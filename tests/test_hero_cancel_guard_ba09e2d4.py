import numpy as np
import pytest
from tavern_ai.hero_cancel_guard_ba09e2d4 import HeroCancelGuard
from tavern_ai.contract import ACTIONS

def mask(*indices):
    x = np.zeros(ACTIONS, dtype=bool)
    x[list(indices)] = True
    return x

def test_override_after_two_hero_cancel_pairs_only_when_end_legal():
    g = HeroCancelGuard()
    m = mask(0,4,5,7)
    assert [g.select(3,a,m) for a in (4,7,5,7)] == [4,7,5,7]
    assert g.select(3,4,m) == 0
    assert g.interventions == 1

def test_never_force_illegal_end():
    g = HeroCancelGuard()
    m = mask(4,7)
    for a in (4,7,4,7):
        g.select(3,a,m)
    assert g.select(3,4,m) == 4 and g.interventions == 0

def test_other_moves_and_new_turn_not_overridden():
    g = HeroCancelGuard()
    m = mask(0,4,7,8)
    for a in (4,7,4,7):
        g.select(3,a,m)
    assert g.select(3,8,m) == 8
    assert g.select(4,4,m) == 4
    assert g.interventions == 0

def test_illegal_proposal_rejected():
    with pytest.raises(ValueError,match="illegal"):
        HeroCancelGuard().select(3,4,mask(0))
