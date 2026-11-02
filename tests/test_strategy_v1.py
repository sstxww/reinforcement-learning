import numpy as np
import pytest
from tavern_ai.baseline import BaselinePolicy

def m(*acts):
    mask=np.zeros(245,dtype=bool)
    mask[list(acts)]=True
    return {"action_mask":mask}

def test_economy_before_optional_action():
    assert BaselinePolicy().act(m(0,9,130),{"turn":3,"actions_used":1})==9

def test_early_upgrade_when_legal():
    assert BaselinePolicy().act(m(0,3,9),{"turn":2,"actions_used":0})==3

def test_bounded_action_budget():
    assert BaselinePolicy().act(m(0,9,130),{"turn":3,"actions_used":36})==0

def test_mandatory_choice_even_at_budget():
    assert BaselinePolicy().act(m(0,30),{"turn":3,"actions_used":99})==30

def test_invalid_budget():
    with pytest.raises(ValueError):
        BaselinePolicy(max_actions_per_turn=0)
