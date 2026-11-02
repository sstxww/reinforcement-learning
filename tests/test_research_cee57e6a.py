"""Public-only policy decision regression tests; live engine tested in workflow."""
import numpy as np
from tavern_ai.research_cee57e6a import ACTIONS, FEATURES, BOARD, HAND, MINION, BoardSwapPolicy

def scene(golden=False,hand_attack=7.,hand_health=7.):
    f=np.zeros(FEATURES,dtype=np.float32)
    m=np.zeros(ACTIONS,dtype=bool)
    f[32],f[33]=1.,.1
    m[0]=m[8]=True
    m[16:23]=True
    for i in range(7):
        off=BOARD+i*MINION
        f[off],f[off+1],f[off+2]=1.,.5,.5
    off=BOARD+4*MINION
    f[off+1],f[off+2],f[off+5]=.1,.1,float(golden)
    f[HAND],f[HAND+1]=1.,1.
    f[HAND+10],f[HAND+11]=hand_attack/10,hand_health/10
    return {"features":f,"action_mask":m}

def test_strong_hand_can_replace_weak_board():
    p=BoardSwapPolicy(4)
    assert p.act(scene(),{"turn":8,"actions_used":7})==20
    assert p.swaps==1

def test_do_not_sell_golden_or_equal_hand():
    p=BoardSwapPolicy(4)
    assert p.act(scene(golden=True),{"turn":8,"actions_used":7})==8
    assert p.act(scene(hand_attack=1.,hand_health=1.),{"turn":9,"actions_used":7})==8

def test_original_plays_upgrades_and_one_swap_cap():
    p=BoardSwapPolicy(4)
    x=scene()
    x["action_mask"][46]=True
    assert p.act(x,{"turn":8,"actions_used":7})==46
    x["action_mask"][46]=False
    assert p.act(x,{"turn":8,"actions_used":7})==20
    assert p.act(x,{"turn":8,"actions_used":8})==8
    x["action_mask"][3]=True
    assert p.act(x,{"turn":9,"actions_used":7})==3

def test_not_full_or_early_turn():
    p=BoardSwapPolicy(4)
    x=scene()
    assert p.act(x,{"turn":5,"actions_used":7})==8
    x["action_mask"][22]=False
    assert p.act(x,{"turn":6,"actions_used":7})==8
