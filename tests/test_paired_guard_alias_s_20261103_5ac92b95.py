"""Synthetic negative evidence tests only; never authentic match receipts."""
from copy import deepcopy
import pytest
from tavern_ai.paired_receipt_gate_v5 import compare

def receipt(policy="model", seed=99521):
    return {
        "schema": 1, "environment": "TavernGym", "completed": True,
        "agent_id": "fixture-not-a-game", "policy": policy,
        "engine_version": "1.1.0",
        "engine_source_hash": "6d8712c93022ba11",
        "seed": seed, "seat": 0, "turns": 14, "decisions": 40,
        "placements": [8, 2, 3, 4, 5, 6, 7, 1],
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": "a" * 64 if policy == "model" else None,
    }

def test_raw_v5_canary_backward_compatible_with_absent_optional_audit_fields():
    output = compare([receipt()], [receipt("baseline")])
    assert output["pure_model_candidate_games"] == 1
    assert output["model_promotion_authorized"] is False

def test_explicit_unassisted_canonical_model_is_accepted():
    candidate = receipt()
    candidate.update(raw_model_only=True, guard_forced_ends=0, fallback_actions=0)
    assert compare([candidate], [receipt("baseline")])["pure_model_candidate_games"] == 1

@pytest.mark.parametrize("field", [
    "guard_forced_ends", "model_guard_forced_end",
    "fallback_actions", "safety_fallbacks",
])
def test_nonzero_real_world_assistance_alias_is_not_raw(field):
    candidate = receipt()
    candidate[field] = 1
    with pytest.raises(ValueError, match="Undisclosed"):
        compare([candidate], [receipt("baseline")])

@pytest.mark.parametrize("field", ["guard_forced_ends", "fallback_actions"])
def test_nested_diagnostic_alias_is_not_raw(field):
    candidate = receipt()
    candidate["opportunity_diagnostics"] = {"counts": {field: 1}}
    with pytest.raises(ValueError, match="Undisclosed"):
        compare([candidate], [receipt("baseline")])

@pytest.mark.parametrize("field", ["guard_forced_ends", "fallback_actions"])
def test_malformed_boolean_guard_counter_is_rejected(field):
    candidate = receipt()
    candidate[field] = False
    with pytest.raises(ValueError, match="Invalid"):
        compare([candidate], [receipt("baseline")])

@pytest.mark.parametrize("value", [False, None, 0, "false"])
def test_explicit_non_raw_flag_is_rejected(value):
    candidate = receipt()
    candidate["raw_model_only"] = value
    with pytest.raises(ValueError, match="Undisclosed"):
        compare([candidate], [receipt("baseline")])

def test_assisted_baseline_is_rejected_too():
    baseline = receipt("baseline")
    baseline["guard_forced_ends"] = 1
    with pytest.raises(ValueError, match="Baseline"):
        compare([receipt()], [baseline])

def test_guarded_model_not_counted_as_raw():
    guarded = receipt("model")
    guarded.update(policy="model_guarded", guarded=True, guard_forced_ends=2)
    summary = compare([guarded], [receipt("baseline")])
    assert summary["guarded_candidate_games"] == 1
    assert summary["pure_model_candidate_games"] == 0
    assert summary["model_promotion_authorized"] is False
