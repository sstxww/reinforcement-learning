import pytest
from tavern_ai.validate_receipt import validate

def good():
    return {"environment":"TavernGym","completed":True,"agent_id":"a1",
            "placements":[1,2,3,4,5,6,7,8],"turns":15,"decisions":31,
            "truncated_combats":0,"turn_limit_end":False}

def test_valid():
    assert validate(good())

def test_valid_scrambled_placements():
    p=good()
    p["placements"]=[8,3,7,1,6,4,2,5]
    assert validate(p)

@pytest.mark.parametrize("field,value",[
    ("completed",False),("agent_id",""),("placements",[1]),
    ("placements",[1,1,3,4,5,6,7,8]),
    ("placements",[8,8,8,8,8,8,8,8]),
    ("placements",[1,2,3,4,5,6,7,True]),
    ("decisions",0),("truncated_combats",1),("turn_limit_end",True)
])
def test_invalid(field,value):
    p=good()
    p[field]=value
    with pytest.raises(ValueError):validate(p)
