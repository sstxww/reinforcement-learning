import numpy as np
import pytest
from tavern_ai.bc_probe_73729553 import FAMILIES, family, features, fit, bc_action, score

def test_action_family_partition_is_exact():
    assert len(FAMILIES)==14
    assert [(i, family(i)) for i in range(245)] == [
        (i, next(j for j,(_,lo,hi) in enumerate(FAMILIES) if lo <= i < hi))
        for i in range(245)
    ]

def test_public_observation_mask_dimensions_and_features():
    f=np.zeros(4017,dtype=np.float32);f[7]=.4
    m=np.zeros(245,dtype=bool);m[[0,8,46]]=True
    x,avail=features(f,m,2)
    assert x.shape==(39,) and avail.sum()==3
    assert x[2]==pytest.approx(.4)
    with pytest.raises(ValueError):features(np.zeros(3227),m,0)
    with pytest.raises(ValueError):features(f,np.zeros(245,dtype=bool),0)

def test_masked_teacher_imitation_stays_legal():
    f=np.zeros(4017,dtype=np.float32)
    m=np.zeros(245,dtype=bool);m[[0,9]]=True
    x,av=features(f,m,0)
    w,report=fit([(x,av,family(9))]*3,steps=25)
    assert report["gradient_updates"]==25
    assert 0 <= score([(x,av,family(9))],w) <= 1
    assert bc_action(f,m,0,w) in (0,9)
    only_choose=np.zeros(245,dtype=bool);only_choose[30]=True
    assert bc_action(f,only_choose,0,w)==30
