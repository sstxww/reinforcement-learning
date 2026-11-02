import pytest
from tavern_ai.contract import ENGINE_HASH
from tavern_ai.validate_receipt import validate

def good():
    return {"schema":1,"environment":"TavernGym","completed":True,"agent_id":"a1",
            "engine_version":"1.1.0","engine_source_hash":ENGINE_HASH,
            "seed":1001,"policy":"baseline",
            "placements":[1,2,3,4,5,6,7,8],"turns":15,"decisions":31,
            "truncated_combats":0,"turn_limit_end":False}

def test_valid():
    assert validate(good())

@pytest.mark.parametrize("field,value",[
    ("completed",False),("agent_id",""),("placements",[1]),
    ("decisions",0),("truncated_combats",1),("turn_limit_end",True),
    ("engine_version","1.0.0"),("engine_source_hash","wrong"),
    ("seed","bad"),("policy","unknown"),("schema",None)
])
def test_invalid(field,value):
    p=good()
    p[field]=value
    with pytest.raises(ValueError):validate(p)

def test_model_requires_provenance():
    p=good()
    p["policy"]="model"
    with pytest.raises(ValueError,match="checkpoint hash"):validate(p)
    p["model_sha256"]="abc123"
    assert validate(p)
