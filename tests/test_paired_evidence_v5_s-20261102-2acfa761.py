"""No game is simulated by these tests: all receipt fixtures are synthetic."""
import copy
import pytest
from tavern_ai.paired_evidence_v5 import paired_summary

SHA = "1" * 64

def row(seed, rank, policy, **extra):
    data = {"environment": "TavernGym", "engine_version": "1.1.0",
            "engine_source_hash": "6d8712c93022ba11", "agent_id": "fixture",
            "policy": policy, "seed": seed, "completed": True,
            "turns": 14, "decisions": 41,
            "placements": [rank] + [x for x in range(1, 9) if x != rank],
            "truncated_combats": 0, "turn_limit_end": False,
            "model_sha256": SHA if policy != "baseline" else None}
    data.update(extra)
    return data

def test_matched_raw_model_is_descriptive_not_champion():
    r = paired_summary([row(101, 6, "baseline"), row(102, 8, "baseline")],
                       [row(102, 8, "model"), row(101, 8, "model")])
    assert r["seeds"] == [101, 102]
    assert r["paired_rank_deltas_candidate_minus_baseline"] == [2, 0]
    assert r["policy_provenance"] == "raw_model"
    assert r["promotion_eligible"] is False

def test_guarded_model_cannot_masquerade_as_raw():
    r = paired_summary([row(101, 5, "baseline")],
                       [row(101, 8, "model", guard_forced_ends=12)])
    assert r["policy_provenance"] == "guarded_or_assisted_model"
    r2 = paired_summary([row(101, 5, "baseline")],
                        [row(101, 8, "model_guarded")])
    assert r2["policy_provenance"] == "guarded_or_assisted_model"

@pytest.mark.parametrize("mutation", ["missing_seed", "duplicate_seed", "wrong_engine",
                                      "not_permutation", "incomplete", "mixed_sha", "fake_policy"])
def test_fail_closed_on_unpaired_or_invalid_evidence(mutation):
    baseline = [row(101, 6, "baseline"), row(102, 7, "baseline")]
    candidate = [row(101, 8, "model"), row(102, 8, "model")]
    if mutation == "missing_seed": candidate.pop()
    elif mutation == "duplicate_seed": candidate[1]["seed"] = 101
    elif mutation == "wrong_engine": candidate[0]["engine_source_hash"] = "different"
    elif mutation == "not_permutation": candidate[0]["placements"] = [8] * 8
    elif mutation == "incomplete": candidate[0]["completed"] = False
    elif mutation == "mixed_sha": candidate[0]["model_sha256"] = "2" * 64
    elif mutation == "fake_policy": candidate[0]["policy"] = "baseline"
    with pytest.raises(ValueError):
        paired_summary(baseline, candidate)
