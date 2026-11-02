import pytest
from tavern_ai.guard_budget_eval import paired_summary

def receipt(seed,cap,rank,decisions=20,interventions=1):
    return {
        "environment":"TavernGym","completed":True,
        "agent_id":"s-20261102-e599fa38","policy":"model_guarded",
        "placements":[rank]+[i for i in range(1,9) if i != rank],
        "turns":15,"decisions":decisions,"truncated_combats":0,
        "turn_limit_end":False,"seed":seed,"model_sha256":"sha",
        "engine_source_hash":"engine",
        "guard_max_turn_actions":cap,"guard_interventions":interventions
    }

def test_paired_and_seed_order():
    low=[receipt(2,16,5,9,2),receipt(1,16,8,10,1)]
    high=[receipt(1,32,6,12,0),receipt(2,32,4,11,0)]
    x=paired_summary(low,high)
    assert x["seeds"]==[1,2]
    assert x["paired_rank_delta_low_minus_high"]==[2,1]
    assert x["low"]["mean_placement"]==6.5
    assert x["high"]["mean_decisions"]==11.5

def test_unpaired():
    with pytest.raises(ValueError,match="Unpaired"):
        paired_summary([receipt(1,16,8)],[receipt(2,32,8)])

def test_wrong_budget():
    with pytest.raises(ValueError,match="budget"):
        paired_summary([receipt(1,32,8)],[receipt(1,32,8)])

def test_duplicate_seed():
    with pytest.raises(ValueError,match="Duplicate"):
        paired_summary([receipt(1,16,8),receipt(1,16,8)],[receipt(1,32,8)])

def test_different_checkpoint():
    a,b=receipt(1,16,8),receipt(1,32,8)
    b["model_sha256"]="different"
    with pytest.raises(ValueError,match="checkpoint"):
        paired_summary([a],[b])

def test_incomplete_game():
    a=receipt(1,16,8)
    a["completed"]=False
    with pytest.raises(ValueError,match="Incomplete"):
        paired_summary([a],[receipt(1,32,8)])
