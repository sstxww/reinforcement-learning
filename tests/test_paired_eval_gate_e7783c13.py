"""Only synthetic negative/format test fixtures, never game results."""
from copy import deepcopy

import pytest

from tavern_ai.contract import ENGINE_HASH
from tavern_ai.paired_eval_gate_e7783c13 import audit_pair


def receipt(seed, policy, seat=0, rank=8):
    places = list(range(1, 9))
    original_index = places.index(rank)
    places[seat], places[original_index] = places[original_index], places[seat]
    return {
        "environment": "TavernGym", "completed": True,
        "agent_id": "synthetic-unit-test-only", "policy": policy,
        "model_sha256": "a" * 64 if policy == "model" else None,
        "seed": seed, "controlled_seat": seat,
        "engine_version": "1.1.0", "engine_source_hash": ENGINE_HASH,
        "placements": places, "turns": 7, "decisions": 25,
        "truncated_combats": 0, "turn_limit_end": False,
    }


def test_paired_seed_seat_statistics():
    b = [receipt(101, "baseline", 0, 7), receipt(101, "baseline", 3, 6)]
    c = [receipt(101, "model", 3, 6), receipt(101, "model", 0, 8)]
    outcome = audit_pair(b, c)
    assert outcome["complete_games"] == 4
    assert outcome["paired_rank_delta_candidate_minus_baseline"] == .5
    assert outcome["promotion_eligible"] is False


@pytest.mark.parametrize("mutate", [
    lambda x: x.update(guard_interventions=1),
    lambda x: x.update(safety_fallback_count=2),
    lambda x: x.update(forced_end_turns=1),
    lambda x: x.update(policy_variant="hero_cancel_guard_v1"),
    lambda x: x.update(model_sha256="b" * 64),
])
def test_guard_and_checkpoint_contamination_rejected(mutate):
    b = [receipt(101, "baseline"), receipt(102, "baseline")]
    c = [receipt(101, "model"), receipt(102, "model")]
    mutate(c[1])
    with pytest.raises(ValueError):
        audit_pair(b, c)


def test_fail_closed_on_unpaired_duplicate_and_tampered_receipts():
    b = [receipt(101, "baseline")]
    c = [receipt(102, "model")]
    with pytest.raises(ValueError, match="pairs"):
        audit_pair(b, c)
    with pytest.raises(ValueError, match="Duplicate"):
        audit_pair(b * 2, [receipt(101, "model")])
    tampered = deepcopy(c[0])
    tampered["placements"] = [8] * 8
    with pytest.raises(ValueError, match="permutation"):
        audit_pair([receipt(102, "baseline")], [tampered])
