"""Synthetic negative tests; these fixtures are NOT game evidence."""
import copy
import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/v7_buy_pair_s_20261103_21a7d8bc.py"
spec = importlib.util.spec_from_file_location("v7_buy_pair", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SID = "s-20261103-21a7d8bc"
SHA = "a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632"


def fixture(policy):
    legal, buys = (10, 5) if policy == "baseline" else (12, 0)
    return {
        "environment": "TavernGym", "completed": True, "agent_id": SID,
        "policy": policy, "seed": 97421, "placements": [8,1,2,3,4,5,6,7],
        "turns": 15, "decisions": 30, "truncated_combats": 0,
        "turn_limit_end": False, "engine_version": "1.1.0",
        "engine_source_hash": "6d8712c93022ba11",
        "model_sha256": SHA if policy == "model" else None,
        "opportunity_summary": {
            "decisions": 30, "buy_legal_decisions": legal,
            "buy_chosen": buys, "conditional_buy_rate_given_legal": buys / legal,
        },
    }


def test_valid_but_no_strength_claim():
    result = module.audit_pair(fixture("baseline"), fixture("model"), SID, SHA)
    assert result["raw_model"]["buys"] == 0
    assert result["model_strength_improved"] is False


@pytest.mark.parametrize("mutation", ["seed", "digest", "fallback", "guard", "rate", "counts", "policy"])
def test_reject_mismatched_or_assisted(mutation):
    b, m = fixture("baseline"), fixture("model")
    if mutation == "seed":
        m["seed"] = 97422
    elif mutation == "digest":
        m["model_sha256"] = "b" * 64
    elif mutation == "fallback":
        m["fallback_actions"] = 1
    elif mutation == "guard":
        m["model_guard_forced_end"] = 1
    elif mutation == "rate":
        m["opportunity_summary"]["conditional_buy_rate_given_legal"] = 1
    elif mutation == "counts":
        m["opportunity_summary"]["buy_chosen"] = 13
    else:
        m["policy"] = "baseline"
    with pytest.raises(ValueError):
        module.audit_pair(b, m, SID, SHA)
