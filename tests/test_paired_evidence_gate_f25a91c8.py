"""Synthetic validator fixtures only: these are NOT game receipts or performance results."""
from __future__ import annotations

from copy import deepcopy

import pytest

from tavern_ai.paired_evidence_gate_f25a91c8 import evaluate_pairs

HASH = "a" * 64
ENGINE = "6d8712c93022ba11"


def synthetic(seed: int, rank: int, policy: str) -> dict:
    return {
        "environment": "TavernGym",
        "completed": True,
        "agent_id": "synthetic-fixture-only",
        "engine_version": "1.1.0",
        "engine_source_hash": ENGINE,
        "seed": seed,
        "seat": 0,
        "policy": policy,
        "placements": [rank] + [r for r in range(1, 9) if r != rank],
        "model_sha256": HASH if policy != "baseline" else None,
        "turns": 12,
        "decisions": 50,
        "truncated_combats": 0,
        "turn_limit_end": False,
        "guard_forced_ends": 0,
        "guarded": False,
    }


def pair():
    return ([synthetic(701, 8, "model"), synthetic(702, 7, "model")],
            [synthetic(701, 6, "baseline"), synthetic(702, 5, "baseline")])


def test_paired_summary_is_deterministic_and_does_not_promote():
    c, b = pair()
    result = evaluate_pairs(c, b, bootstrap_draws=100)
    assert result["pairs"] == 2
    assert result["paired_rank_deltas"] == [2, 2]
    assert result["paired_mean_placement_delta"] == 2
    assert result["paired_bootstrap_95pct_interval"] == [2, 2]
    assert result["champion_promoted"] is False
    assert result["signal_for_manual_review_only"] is False


@pytest.mark.parametrize("mutation", [
    lambda c, b: c[0].update(policy="model_guarded"),
    lambda c, b: c[0].update(guarded=True),
    lambda c, b: c[0].update(guard_forced_ends=1),
    lambda c, b: c[0].update(raw_model_only=False),
    lambda c, b: c[0].update(safety_fallbacks=2),
    lambda c, b: c[0].update(turn_limit_end=True),
    lambda c, b: c[0].update(truncated_combats=1),
    lambda c, b: c[0].update(engine_source_hash="wrong"),
    lambda c, b: c[0].update(placements=[8] * 8),
    lambda c, b: c[0].update(model_sha256="b" * 64),
    lambda c, b: c[1].update(seed=701),
    lambda c, b: b[1].update(seed=703),
])
def test_fail_closed_for_assistance_corruption_or_unmatched_pairs(mutation):
    c, b = pair()
    mutation(c, b)
    with pytest.raises(ValueError):
        evaluate_pairs(c, b, bootstrap_draws=100)


def test_reject_one_pair_and_invalid_bootstrap():
    c, b = pair()
    with pytest.raises(ValueError, match="at least two"):
        evaluate_pairs(c[:1], b[:1])
    with pytest.raises(ValueError, match="bootstrap_draws"):
        evaluate_pairs(c, b, bootstrap_draws=0)


def test_seat_rotation_is_paired_by_seat_not_only_seed():
    c, b = pair()
    c[0]["seat"] = 4
    b[0]["seat"] = 4
    result = evaluate_pairs(c, b, bootstrap_draws=100)
    assert result["seed_seat_pairs"][0] == {"seed": 701, "seat": 4}
    # Same eight-player placements but a different controlled seat changes the score.
    assert result["paired_rank_deltas"][0] == 0


def test_arm_order_does_not_affect_result():
    c, b = pair()
    assert evaluate_pairs(c, b, bootstrap_draws=100) == evaluate_pairs(
        deepcopy(list(reversed(c))), deepcopy(list(reversed(b))), bootstrap_draws=100
    )
