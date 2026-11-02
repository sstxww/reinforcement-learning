"""Synthetic negative-control tests only; NEVER real match or win evidence."""
import pytest
from tavern_ai.paired_receipt_gate_v5 import compare


def row(policy="model", **extra):
    data = {
        "schema": 1, "environment": "TavernGym", "completed": True,
        "engine_version": "1.1.0",
        "engine_source_hash": "6d8712c93022ba11",
        "agent_id": "synthetic-only", "policy": policy,
        "seed": 99412, "seat": 0, "turns": 12, "decisions": 40,
        "placements": [8, 1, 2, 3, 4, 5, 6, 7],
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": "a" * 64 if policy != "baseline" else None,
    }
    data.update(extra)
    return data


@pytest.mark.parametrize("field", [
    "guard_interventions", "guard_forced_ends", "fallback_actions",
    "model_guard_forced_end", "safety_override_count",
    "guard_override_count",
])
def test_unreported_guard_counter_cannot_be_raw_model(field):
    # Before fix, these real-source counter spellings were omitted by the gate.
    with pytest.raises(ValueError, match="Undisclosed"):
        compare([row(**{field: 1})], [row(policy="baseline")])


@pytest.mark.parametrize("container", [
    "opportunity_diagnostics", "opportunity_summary",
])
def test_nested_interventions_are_not_raw_evidence(container):
    payload = ({"counts": {"guard_interventions": 1}} if container ==
               "opportunity_diagnostics" else {"guard_interventions": 1})
    with pytest.raises(ValueError, match="Undisclosed"):
        compare([row(**{container: payload})], [row(policy="baseline")])


def test_declared_assisted_variant_with_zero_interventions_is_diagnostic():
    result = compare([
        row(policy_variant="hero_cancel_guard_v1", guard_interventions=0)
    ], [row(policy="baseline")])
    assert result["guarded_candidate_games"] == 1
    assert result["pure_model_candidate_games"] == 0
    assert result["evidence_status"] == "diagnostic_guarded_not_promotable"
    assert result["model_promotion_authorized"] is False


def test_explicit_raw_probe_with_zero_guard_stays_raw():
    report = compare([
        row(policy_variant="raw_ppo_model", guard_interventions=0)
    ], [row(policy="baseline")])
    assert report["pure_model_candidate_games"] == 1
    assert report["guarded_candidate_games"] == 0


@pytest.mark.parametrize("value", [-1, 0.5, True, "1"])
def test_malformed_guard_counter_fails_closed(value):
    with pytest.raises(ValueError, match="Invalid guard"):
        compare([row(guard_interventions=value)], [row(policy="baseline")])


@pytest.mark.parametrize("value", [True, "", {}, 3])
def test_malformed_variant_fails_closed(value):
    with pytest.raises(ValueError, match="Malformed policy variant"):
        compare([row(policy_variant=value)], [row(policy="baseline")])
