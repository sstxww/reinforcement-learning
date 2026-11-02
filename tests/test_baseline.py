import numpy as np
import pytest
from tavern_ai.baseline import BaselinePolicy

def mask(*actions):
    m=np.zeros(245,dtype=bool)
    m[list(actions)]=True
    return {"action_mask":m}

def test_mandatory_choice():
    assert BaselinePolicy().act(mask(0,8,30),{"turn":2})==30

def test_legal_buy_and_end():
    p=BaselinePolicy()
    assert p.act(mask(0,9),{"turn":3})==9
    assert p.act(mask(0),{"turn":3})==0

def test_plays_before_buying():
    assert BaselinePolicy().act(mask(0,9,46),{"turn":1})==46

def test_action_budget():
    assert BaselinePolicy().act(mask(0,8),{"actions_used":90})==0

def test_empty_mask():
    with pytest.raises(ValueError):BaselinePolicy().act(mask())
