"""No synthetic test records may be used as real-game receipts."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "paired_gate", Path(__file__).resolve().parents[1] / "scripts" / "paired_receipt_audit_f17ed915.py"
)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def receipt(seed: int, policy: str, rank: int = 8, **extra):
    places = [rank] + [n for n in range(1, 9) if n != rank]
    row = {
        "schema": 1, "environment": "TavernGym", "engine_version": "1.1.0",
        "engine_source_hash": "6d8712c93022ba11", "completed": True,
        "policy": policy, "placements": places, "seed": seed,
        "turns": 16, "decisions": 40, "agent_id": "test-fixture",
        "truncated_combats": 0, "turn_limit_end": False,
        "git_sha": "a" * 40,
        "model_sha256": "b" * 64 if policy == "model" else None,
    }
    row.update(extra)
    return row


def test_three_real_style_pairs_have_descriptive_delta_only():
    base = [receipt(99125, "baseline", 6), receipt(99126, "baseline"), receipt(99127, "baseline")]
    model = [receipt(s, "model") for s in (99125, 99126, 99127)]
    output = gate.audit(base, model, training_seeds={42, 47})
    assert output["pairs"] == 3
    assert output["baseline"]["mean_rank"] == pytest.approx(7.333333333)
    assert output["candidate"]["mean_rank"] == 8
    assert output["paired_rank_delta_candidate_minus_baseline"] == pytest.approx(2 / 3)
    assert output["fallback_and_illegal_action_counters"].startswith("unknown")
    assert output["champion_promotion_authorized"] is False


@pytest.mark.parametrize("update", [
    {"completed": False}, {"placements": [8] * 8}, {"engine_source_hash": "tampered"},
    {"truncated_combats": 1}, {"turn_limit_end": True},
    {"decisions": 0}, {"git_sha": ""}, {"fallback_actions": 1},
])
def test_invalid_or_guarded_match_rejected(update):
    with pytest.raises(ValueError):
        gate.audit([receipt(1, "baseline", 4)], [receipt(1, "model", **update)])


def test_unpaired_or_duplicate_seeds_rejected():
    with pytest.raises(ValueError, match="Unpaired"):
        gate.audit([receipt(1, "baseline")], [receipt(2, "model")])
    with pytest.raises(ValueError, match="Duplicate"):
        gate.audit([receipt(1, "baseline"), receipt(1, "baseline")], [receipt(1, "model")])


def test_source_or_model_mismatch_and_leakage_rejected():
    with pytest.raises(ValueError, match="source commits"):
        gate.audit([receipt(1, "baseline")], [receipt(1, "model", git_sha="d" * 40)])
    with pytest.raises(ValueError, match="weights"):
        gate.audit([receipt(1, "baseline"), receipt(2, "baseline")],
                   [receipt(1, "model"), receipt(2, "model", model_sha256="c" * 64)])
    with pytest.raises(ValueError, match="leakage"):
        gate.audit([receipt(1, "baseline")], [receipt(1, "model")], training_seeds={1})


def test_explicit_all_zero_counters_are_reported_without_inventing_them():
    zero = {"forced_end_turns": 0, "baseline_fallback_actions": 0,
            "fallback_actions": 0, "illegal_actions": 0}
    out = gate.audit([receipt(1, "baseline", **zero)], [receipt(1, "model", **zero)])
    assert out["fallback_and_illegal_action_counters"] == "explicit_all_zero"
    assert out["raw_unassisted_model_performance_established"] is True


def test_wilson_bounds_with_zero_success_are_not_zero_width():
    low, high = gate.wilson_95(0, 3)
    assert low == 0
    assert high > 0.5
