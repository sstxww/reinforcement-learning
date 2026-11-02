"""Regression tests for the isolated V5 paired evaluation gate."""
import copy
import pytest

from tavern_ai.paired_receipt_gate_f26b28e0 import summarize_pairs


def receipt(seed, policy):
    return {
        "environment": "TavernGym", "completed": True,
        "agent_id": "s-20261102-f26b28e0", "policy": policy, "seed": seed,
        "turns": 15, "decisions": 44,
        "placements": [8, 1, 2, 3, 4, 5, 6, 7] if policy == "model"
                      else [6, 1, 2, 3, 4, 5, 7, 8],
        "engine_version": "1.1.0", "engine_source_hash": "6d8712c93022ba11",
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": "a" * 64 if policy == "model" else None,
    }


def test_descriptive_paired_rank_and_no_unproved_promotion():
    out = summarize_pairs([receipt(11, "model"), receipt(12, "model")],
                          [receipt(11, "baseline"), receipt(12, "baseline")])
    assert out["games_per_arm"] == 2
    assert out["mean_paired_rank_delta"] == 2
    assert out["model_top4_rate"] == 0
    assert out["promotion_eligible"] is False
    assert out["pure_model_play_verified"] is False


@pytest.mark.parametrize("edit", [
    lambda m, b: b[0].update(seed=15),
    lambda m, b: m[0].update(completed=False),
    lambda m, b: m[0].update(policy="baseline"),
    lambda m, b: m[0].update(model_sha256="bad"),
    lambda m, b: m[0].update(placements=[8] * 8),
    lambda m, b: b[0].update(engine_source_hash="different"),
    lambda m, b: b[0].update(model_sha256="b" * 64),
])
def test_fail_closed_on_invalid_pairs(edit):
    model, baseline = [receipt(11, "model")], [receipt(11, "baseline")]
    edit(model, baseline)
    with pytest.raises(ValueError):
        summarize_pairs(model, baseline)


def test_no_mixing_candidate_weights():
    with pytest.raises(ValueError, match="Mixed model"):
        rows = [receipt(11, "model"), receipt(12, "model")]
        rows[1]["model_sha256"] = "b" * 64
        summarize_pairs(rows, [receipt(11, "baseline"), receipt(12, "baseline")])


def test_registry_digest_required():
    m, b = [receipt(11, "model")], [receipt(11, "baseline")]
    registry = {"engine": {"version": "1.1.0", "source_hash": "6d8712c93022ba11"},
                "candidates": [{"checkpoint_sha256": "b" * 64}]}
    with pytest.raises(ValueError, match="absent"):
        summarize_pairs(m, b, registry)


def test_fallback_reporting_prevents_raw_model_claim():
    m, b = [receipt(11, "model")], [receipt(11, "baseline")]
    m[0]["safety_fallback_count"] = 2
    report = summarize_pairs(m, b)
    assert report["fallback_telemetry_complete"]
    assert report["fallback_reported"]
    assert not report["pure_model_play_verified"]
