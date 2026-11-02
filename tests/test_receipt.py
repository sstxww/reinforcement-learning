import pytest
from tavern_ai.validate_receipt import validate

def good():
    return {"environment":"TavernGym","completed":True,"agent_id":"a1",
            "placements":[1,2,3,4,5,6,7,8],"turns":15,"decisions":31,
            "truncated_combats":0,"turn_limit_end":False}

def test_valid():
    assert validate(good())

@pytest.mark.parametrize("field,value",[
    ("completed",False),("agent_id",""),("placements",[1]),
    ("decisions",0),("truncated_combats",1),("turn_limit_end",True)
])
def test_invalid(field,value):
    p=good()
    p[field]=value
    with pytest.raises(ValueError):validate(p)
