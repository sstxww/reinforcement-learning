"""Synthetic regressions for the P1 paired-game evidence gate (not real games)."""
from __future__ import annotations

import copy
import pytest

from tavern_ai.paired_evidence_s_6fc22e71 import compare

HASH_A = "a" * 64
HASH_B = "b" * 64


def receipt(seed: int = 19111, seat: int = 0, rank: int = 8,
            policy: str = "model", guard: int | None = 0) -> dict:
    places = list(range(1, 9))
    index = places.index(rank)
    places[seat], places[index] = places[index], places[seat]
    r = {
        "schema": 1, "environment": "TavernGym",
        "engine_version": "1.1.0", "engine_source_hash": "6d8712c93022ba11",
        "policy": policy, "seed": seed, "seat": seat, "completed": True,
        "turns": 12, "decisions": 49, "placements": places,
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": HASH_A if policy == "model" else None,
    }
    if policy == "model":
        r["policy_variant"] = "raw_ppo_model"
    if guard is not None and policy == "model":
        r["guard_interventions"] = guard
    return r


def test_paired_real_receipt_shape_and_rank_delta():
    candidate = [receipt(19111, rank=8), receipt(19112, rank=7)]
    baseline = [receipt(19112, rank=6, policy="baseline"),
                receipt(19111, rank=7, policy="baseline")]
    result = compare(candidate, baseline)
    assert result["games_per_arm"] == 2
    assert result["candidate_ranks"] == [8, 7]
    assert result["baseline_ranks"] == [7, 6]
    assert result["candidate_minus_baseline_mean_rank"] == 1
    assert result["paired_mean_rank_delta_bootstrap_95pct"] == [1, 1]
    assert result["candidate_top4_rate"] == 0
    assert result["guard_evidence"] == "explicit_no_fallback"
    assert result["eligible_for_raw_model_claim"] is True
    assert result["champion_promoted"] is False


def test_controlled_seat_changes_extracted_rank():
    result = compare([receipt(19221, seat=3, rank=2)],
                     [receipt(19221, seat=3, rank=5, policy="baseline")])
    assert result["seed_seat_pairs"] == [{"seed": 19221, "seat": 3}]
    assert result["candidate_ranks"] == [2]
    assert result["baseline_ranks"] == [5]
    assert result["candidate_minus_baseline_mean_rank"] == -3


def test_unreported_guard_is_not_raw_model_evidence():
    r = compare([receipt(1, guard=None)], [receipt(1, policy="baseline")])
    assert r["guard_evidence"] == "guard_status_unknown"
    assert r["eligible_for_raw_model_claim"] is False
    assert r["reported_guard_interventions_max_per_game"] == [None]


def test_nonzero_guard_never_passes_raw_model_gate():
    r = compare([receipt(1, guard=12)], [receipt(1, policy="baseline")])
    assert r["guard_evidence"] == "guarded"
    assert r["eligible_for_raw_model_claim"] is False
    assert r["reported_guard_interventions_max_per_game"] == [12]


def test_any_nonzero_guard_field_blocks_raw_claim():
    model = receipt(1)
    model["safety_fallback_count"] = 3
    result = compare([model], [receipt(1, policy="baseline")])
    assert result["guard_evidence"] == "guarded"


@pytest.mark.parametrize("mutation,error", [
    ({"completed": False}, "Incomplete"),
    ({"turn_limit_end": True}, "Incomplete"),
    ({"truncated_combats": 1}, "Combat"),
    ({"engine_version": "1.0.0"}, "engine"),
    ({"engine_source_hash": "different"}, "engine"),
    ({"environment": "mock"}, "TavernGym"),
    ({"policy": "baseline"}, "Expected model"),
    ({"model_sha256": "bad"}, "SHA256"),
    ({"seed": True}, "seed"),
    ({"seat": 9}, "seat"),
    ({"turns": 0}, "turns"),
    ({"guard_interventions": -1}, "guard_interventions"),
])
def test_bad_candidate_receipt_rejected(mutation, error):
    candidate = receipt()
    candidate.update(mutation)
    with pytest.raises(ValueError, match=error):
        compare([candidate], [receipt(policy="baseline")])


def test_malformed_placements_rejected():
    c = receipt()
    c["placements"][0] = c["placements"][1]
    with pytest.raises(ValueError, match="permutation"):
        compare([c], [receipt(policy="baseline")])


def test_duplicate_seed_seat_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        compare([receipt(), receipt()], [receipt(policy="baseline")])


def test_mismatched_seed_or_seat_rejected():
    with pytest.raises(ValueError, match="identical"):
        compare([receipt()], [receipt(seed=19112, policy="baseline")])


def test_mixed_checkpoint_identity_rejected():
    second = receipt(seed=19112)
    second["model_sha256"] = HASH_B
    with pytest.raises(ValueError, match="checkpoint identities"):
        compare([receipt(), second], [receipt(policy="baseline"),
                                        receipt(seed=19112, policy="baseline")])


def test_empty_arms_rejected():
    with pytest.raises(ValueError, match="at least one"):
        compare([], [receipt(policy="baseline")])


def test_cannot_pretend_baseline_is_model():
    with pytest.raises(ValueError, match="Expected model"):
        compare([receipt(policy="baseline")], [receipt(policy="baseline")])



def test_actual_main_v5_1408_four_paired_games_not_misreported_as_raw():
    """Read authentic main receipts, not synthetic fixtures or mock match results.

    Three older model-game receipts do NOT record safety guard status, so a
    combined four-game report must not silently assert all-raw PPO evidence.
    """
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    folder = root / "experiments" / "s-20261102-68099929"
    seeds = (99125, 99126, 99127, 99128)
    candidate = [
        json.loads((folder / f"{'002' if seed < 99128 else '003'}-model-{seed}.json").read_text("utf-8"))
        for seed in seeds
    ]
    baseline = [
        json.loads((folder / f"{'002' if seed < 99128 else '003'}-baseline-{seed}.json").read_text("utf-8"))
        for seed in seeds
    ]
    r = compare(candidate, baseline)
    assert r["games_per_arm"] == 4
    assert r["model_sha256"] == "a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632"
    assert r["candidate_ranks"] == [8, 8, 8, 8]
    assert r["baseline_ranks"] == [6, 8, 8, 8]
    assert r["candidate_minus_baseline_mean_rank"] == 0.5
    assert r["guard_status_unknown_games"] == 4
    assert r["guard_evidence"] == "guard_status_unknown"
    assert r["eligible_for_raw_model_claim"] is False
    assert r["champion_promoted"] is False



def test_old_receipt_with_zero_guard_but_no_variant_is_still_unknown():
    model = receipt()
    del model["policy_variant"]
    r = compare([model], [receipt(policy="baseline")])
    assert r["guard_evidence"] == "guard_status_unknown"
    assert not r["eligible_for_raw_model_claim"]


@pytest.mark.parametrize("variant", [
    "model_with_explicit_buy_override", "hero_cancel_guard_v1",
    "hybrid_model", "baseline_fallback_assisted", "rule_assisted_model",
])
def test_assisted_model_variant_cannot_masquerade_as_raw(variant):
    model = receipt()
    model["policy_variant"] = variant
    r = compare([model], [receipt(policy="baseline")])
    assert r["guard_evidence"] == "guarded"
    assert not r["eligible_for_raw_model_claim"]


def test_unrecognized_policy_variant_is_not_raw():
    model = receipt()
    model["policy_variant"] = "new_experimental_model"
    assert compare([model], [receipt(policy="baseline")])["guard_evidence"] == "guard_status_unknown"
