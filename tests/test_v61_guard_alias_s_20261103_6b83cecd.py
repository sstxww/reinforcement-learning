"""V6.1 synthetic-only regression tests; none are TavernGym match receipts."""
from copy import deepcopy

import pytest

from tavern_ai.paired_receipt_gate_v5 import compare


def receipt(policy, seed=99631):
    return {
        "schema": 1, "environment": "TavernGym", "completed": True,
        "engine_version": "1.1.0",
        "engine_source_hash": "6d8712c93022ba11",
        "agent_id": "synthetic-unit-test-only", "policy": policy,
        "seed": seed, "seat": 0, "turns": 16, "decisions": 60,
        "placements": [8, 2, 3, 4, 5, 6, 7, 1],
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": "a" * 64 if policy == "model" else None,
    }


@pytest.mark.parametrize("counter", ["guard_forced_ends", "fallback_actions"])
def test_nonzero_flat_assistance_alias_rejected_as_raw(counter):
    candidate = receipt("model")
    candidate[counter] = 1
    with pytest.raises(ValueError, match="Undisclosed guard/fallback"):
        compare([candidate], [receipt("baseline")])


@pytest.mark.parametrize("counter", ["guard_forced_ends", "fallback_actions"])
def test_nonzero_nested_assistance_alias_rejected_as_raw(counter):
    candidate = receipt("model")
    candidate["opportunity_diagnostics"] = {"counts": {counter: 1}}
    with pytest.raises(ValueError, match="Undisclosed guard/fallback"):
        compare([candidate], [receipt("baseline")])


@pytest.mark.parametrize("counter", ["guard_forced_ends", "fallback_actions"])
def test_baseline_with_assistance_alias_rejected(counter):
    baseline = receipt("baseline")
    baseline[counter] = 1
    with pytest.raises(ValueError, match="Baseline receipt"):
        compare([receipt("model")], [baseline])


@pytest.mark.parametrize("value", [-1, 1.5, True, "1"])
def test_invalid_counter_values_fail_closed(value):
    candidate = receipt("model")
    candidate["fallback_actions"] = value
    with pytest.raises(ValueError, match="Invalid guard/fallback"):
        compare([candidate], [receipt("baseline")])


def test_explicitly_guarded_alias_is_diagnostic_never_promoted():
    candidate = receipt("model")
    candidate["guarded"] = True
    candidate["fallback_actions"] = 1
    result = compare([candidate], [receipt("baseline")])
    assert result["guarded_candidate_games"] == 1
    assert result["pure_model_candidate_games"] == 0
    assert result["evidence_status"] == "diagnostic_guarded_not_promotable"
    assert result["model_promotion_authorized"] is False


def test_zero_aliases_preserve_raw_model_path():
    candidate = receipt("model")
    candidate["fallback_actions"] = 0
    candidate["guard_forced_ends"] = 0
    candidate["opportunity_diagnostics"] = {"counts": {"fallback_actions": 0}}
    result = compare([candidate], [receipt("baseline")])
    assert result["pure_model_candidate_games"] == 1
    assert result["guarded_candidate_games"] == 0


def test_fixture_is_not_source_of_true_game():
    assert receipt("model")["agent_id"] == "synthetic-unit-test-only"
