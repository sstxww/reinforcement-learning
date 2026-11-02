import numpy as np
import pytest
from tavern_ai.economy_gate_s_20261102_13020d89 import EconomyGatePolicy, summary

def obs(*legal,board=1,health=40):
    f=np.zeros(4017,dtype=np.float32)
    f[5]=health/40; f[10]=2/6; f[33]=board/7
    m=np.zeros(245,dtype=bool);m[list(legal)]=True
    return {"features":f,"action_mask":m}

def test_deferral():
    p=EconomyGatePolicy(5)
    assert p.act(obs(0,3,8,board=1),{"turn":2})==8
    assert p.deferred==1

def test_full_board_levels():
    assert EconomyGatePolicy(2).act(obs(0,3,8,board=4),{"turn":2})==3

def test_health_gate():
    p=EconomyGatePolicy(5)
    assert p.act(obs(0,3,8,board=4,health=20),{"turn":7})==8
    assert p.act(obs(0,3,8,board=4,health=30),{"turn":7})==3

def test_mandatory_choice_and_budget():
    p=EconomyGatePolicy(5)
    assert p.act(obs(0,3,8,30),{"turn":2})==30
    assert p.act(obs(0,3,8),{"turn":2,"actions_used":90})==0

def test_mask_controls_policy():
    p=EconomyGatePolicy(5)
    assert p.act(obs(0,3),{"turn":2})==3
    assert p.act(obs(0,8),{"turn":2})==8

def test_invalid_contract():
    with pytest.raises(ValueError):
        EconomyGatePolicy(2).act({"features":np.zeros(10),"action_mask":obs(0)["action_mask"]})

def test_summary():
    row={"placements":[8,1,2,3,4,5,6,7],"deferred_upgrades":0,"budget_guard_ends":0}
    assert summary([row])["mean_rank"]==8
