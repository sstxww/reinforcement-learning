import numpy as np
import pytest
from tavern_ai.bc_s_20261102_1f73f4a5 import choose_legal, encode_features

def test_illegal_highest_logit_is_masked():
    logits=np.zeros(245,dtype=np.float32)
    logits[17]=99
    logits[9]=1
    mask=np.zeros(245,dtype=bool)
    mask[[0,9]]=True
    assert choose_legal(logits,mask,used=1,guard=False)==(9,False)

def test_guard_is_explicit_and_countable():
    logits=np.zeros(245)
    logits[9]=1
    mask=np.zeros(245,dtype=bool)
    mask[[0,9]]=True
    assert choose_legal(logits,mask,used=85,guard=True)==(0,True)
    assert choose_legal(logits,mask,used=85,guard=False)==(9,False)

def test_empty_mask_and_bad_logits_rejected():
    with pytest.raises(ValueError):
        choose_legal(np.ones(245),np.zeros(245,dtype=bool))
    with pytest.raises(ValueError):
        choose_legal(np.ones(244),np.ones(245,dtype=bool))

def test_public_encoding_dimensions_and_finiteness():
    arr=np.zeros(4017,dtype=np.float32)
    x=encode_features(arr,4,80)
    assert x.shape==(4019,)
    assert x[-2]==pytest.approx(4/30)
    assert x[-1]==pytest.approx(.8)
    assert np.isfinite(x).all()
    arr[5]=np.nan
    with pytest.raises(ValueError):
        encode_features(arr,4,80)
