import numpy as np
import pytest
from tavern_ai.teacher_clone_s4d619f26 import ACTIONS, FEATURES, GROUPS, family, encode

def test_real_pinned_action_semantics():
    assert [i for _,lo,hi in GROUPS for i in range(lo,hi)]==list(range(245))
    assert family(0)=="end" and family(8)=="buy"
    assert family(16)=="sell" and family(22)=="sell"
    assert family(23)=="activate" and family(30)=="choose"
    assert family(46)=="play" and family(126)=="magnetize"
    assert family(195)=="magnetize" and family(196)=="move"
    with pytest.raises(ValueError): family(245)

def test_public_only_and_mask_encoding():
    f=np.zeros(FEATURES,dtype=np.float32)
    m=np.zeros(ACTIONS,dtype=bool); m[[0,8,46]]=True
    before=encode(f,m)
    f[42:]=np.arange(FEATURES-42,dtype=np.float32)*0.01
    assert len(before)==287
    np.testing.assert_array_equal(before,encode(f,m))
    assert before[-245:].sum()==3

def test_rejects_invalid_public_observations():
    f=np.zeros(FEATURES,dtype=np.float32)
    m=np.zeros(ACTIONS,dtype=bool)
    with pytest.raises(ValueError): encode(f,m)
    m[0]=True
    with pytest.raises(ValueError): encode(f[:-1],m)
    f[1]=np.inf
    with pytest.raises(ValueError): encode(f,m)
