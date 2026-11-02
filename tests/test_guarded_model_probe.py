import numpy as np
import pytest
from tavern_ai.guarded_model_probe import choose_guarded

def mask(*indices):
    a = np.zeros(245, dtype=bool)
    a[list(indices)] = True
    return a

def test_regular_action_preserved():
    assert choose_guarded(mask(0,11),11,31,32) == (11,False)

def test_guard_end_turn():
    assert choose_guarded(mask(0,11),11,32,32) == (0,True)
    assert choose_guarded(mask(0,11),0,99,32) == (0,False)
    assert choose_guarded(mask(11),11,99,32) == (11,False)

@pytest.mark.parametrize("proposal",[-1,12,245])
def test_invalid_proposal_fails_closed(proposal):
    with pytest.raises(ValueError,match="illegal action"):
        choose_guarded(mask(0,11),proposal,100,32)

@pytest.mark.parametrize("used,budget",[(1,0),(-1,32)])
def test_invalid_budget(used,budget):
    with pytest.raises(ValueError):
        choose_guarded(mask(0,11),11,used,budget)

def test_empty_mask_fails_closed():
    with pytest.raises(ValueError):
        choose_guarded(mask(),11,0,32)
