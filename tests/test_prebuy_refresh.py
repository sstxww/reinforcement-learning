import numpy as np
import pytest
from tavern_ai.prebuy_refresh import PreBuyRefreshPolicy, summary

def obs(*xs):
    mask=np.zeros(245,dtype=bool)
    mask[list(xs)]=True
    return {"action_mask":mask}

def test_midgame_refresh_before_buy_then_buy():
    p=PreBuyRefreshPolicy()
    assert p.act(obs(0,1,8), turn=5, actions_used=1)==1
    assert p.act(obs(0,1,8), turn=5, actions_used=2)==8
    assert p.total_refreshes == 1
    assert p.opportunities == 2

def test_refresh_cap_resets_next_turn():
    p=PreBuyRefreshPolicy()
    assert p.act(obs(0,1,8), turn=4, actions_used=3)==1
    assert p.act(obs(0,1,8), turn=5, actions_used=3)==1

def test_no_refresh_with_mandatory_choice_or_lack_of_refresh_mask():
    p=PreBuyRefreshPolicy()
    assert p.act(obs(0,1,30,8), turn=5, actions_used=0)==30
    assert p.act(obs(0,8), turn=5, actions_used=1)==8
    assert p.total_refreshes == 0

def test_pre_midgame_not_refreshed_and_safety_budget():
    p=PreBuyRefreshPolicy()
    assert p.act(obs(0,1,8), turn=3, actions_used=1)==8
    assert p.act(obs(0,1,8), turn=6, actions_used=80)==8

def test_invalid_mask_and_min_turn():
    with pytest.raises(ValueError):
        PreBuyRefreshPolicy(min_turn=-1)
    with pytest.raises(ValueError):
        PreBuyRefreshPolicy().act(obs(), turn=5, actions_used=0)

def test_summary():
    s=summary([{"seed":1,"placements":[2,3,4,5,6,7,8,1]},
               {"seed":2,"placements":[8,3,4,5,6,7,1,2]}])
    assert s["mean_rank"]==5
    assert s["first_place_rate"]==0
    assert s["top4_rate"]==0.5
    with pytest.raises(ValueError):summary([])
