"""Synthetic mutation tests, NOT real completed TavernGym games."""
import copy
import pytest

from tavern_ai.contract import ENGINE_HASH
from tavern_ai.opportunity_receipt_gate_s8d23519f import audit


def synthetic_fixture():
    trace = [
        {"turn": 1, "action": 8, "family": "buy", "buy_legal": True,
         "legal_buy_count": 3, "same_public_state_as_prior": False},
        {"turn": 1, "action": 2, "family": "freeze", "buy_legal": False,
         "legal_buy_count": 0, "same_public_state_as_prior": False},
        {"turn": 1, "action": 0, "family": "end_turn", "buy_legal": False,
         "legal_buy_count": 0, "same_public_state_as_prior": False},
    ]
    return {
        "environment": "TavernGym", "engine_version": "1.1.0",
        "engine_source_hash": ENGINE_HASH, "agent_id": "synthetic-only",
        "policy": "baseline", "model_sha256": None, "seed": 1,
        "completed": True, "turns": 1, "decisions": 3,
        "placements": [1, 2, 3, 4, 5, 6, 7, 8],
        "truncated_combats": 0, "turn_limit_end": False,
        "model_guard_forced_end": 0,
        "trace_first_32": trace,
        "opportunity_summary": {
            "decisions": 3, "by_action_family": {
                "buy": 1, "freeze": 1, "end_turn": 1,
                "buy_legal_decisions": 1, "all_end_turns": 1,
            },
            "buy_legal_decisions": 1, "buy_chosen": 1, "all_end_turns": 1,
            "end_while_buy_legal": 0, "distinct_turns_with_legal_buy": 1,
            "unique_public_states_with_legal_buy": 1,
            "turns_with_end_while_buy_legal": 0,
            "consecutive_identical_public_observation": 0,
            "conditional_buy_rate_given_legal": 1.0,
            "conditional_end_rate_given_legal_buy": 0.0,
        },
    }


def test_consistent_synthetic_telemetry():
    r = audit(synthetic_fixture())
    assert r["legal_buy_decisions"] == r["buy_chosen"] == 1
    assert r["raw_unassisted"] is True


@pytest.mark.parametrize("edit", [
    lambda r: r["opportunity_summary"].update(decisions=4),
    lambda r: r["opportunity_summary"]["by_action_family"].update(freeze=2),
    lambda r: r["opportunity_summary"].update(buy_chosen=0),
    lambda r: r["opportunity_summary"].update(buy_legal_decisions=0),
    lambda r: r["opportunity_summary"].update(conditional_buy_rate_given_legal=0.5),
    lambda r: r["opportunity_summary"].update(distinct_turns_with_legal_buy=5),
    lambda r: r["opportunity_summary"].update(all_end_turns=2),
    lambda r: r["trace_first_32"][1].update(family="other"),
    lambda r: r["trace_first_32"][0].update(buy_legal=False),
    lambda r: r["trace_first_32"][0].update(legal_buy_count=0),
    lambda r: r.update(model_guard_forced_end=1),
    lambda r: r.update(policy_variant="hero_cancel_guard_v1"),
    lambda r: r["trace_first_32"][0].update(action=999),
    lambda r: r["opportunity_summary"]["by_action_family"].update(hallucinated=1),
])
def test_reject_internally_contradictory_synthetic_data(edit):
    rec = copy.deepcopy(synthetic_fixture())
    edit(rec)
    with pytest.raises(ValueError):
        audit(rec)


def test_zero_buy_legal_requires_null_rates():
    rec = synthetic_fixture()
    rec["opportunity_summary"]["buy_legal_decisions"] = 0
    rec["opportunity_summary"]["by_action_family"].pop("buy_legal_decisions")
    rec["opportunity_summary"]["by_action_family"].pop("buy")
    rec["opportunity_summary"]["by_action_family"]["other"] = 1
    rec["opportunity_summary"]["buy_chosen"] = 0
    rec["opportunity_summary"]["distinct_turns_with_legal_buy"] = 0
    rec["opportunity_summary"]["unique_public_states_with_legal_buy"] = 0
    rec["opportunity_summary"]["conditional_buy_rate_given_legal"] = None
    rec["opportunity_summary"]["conditional_end_rate_given_legal_buy"] = None
    rec["trace_first_32"][0].update(action=4, family="other", buy_legal=False, legal_buy_count=0)
    assert audit(rec)["legal_buy_decisions"] == 0
