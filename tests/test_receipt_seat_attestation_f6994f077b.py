"""Synthetic regressions for the genuine rotated-seat receipt audit.

These fixtures are NOT played games or performance evidence.
"""
import copy

import pytest

from tavern_ai.contract import ENGINE_HASH
from tavern_ai.receipt_integrity import validate_integrity


def receipt():
    return {
        "environment": "TavernGym",
        "completed": True,
        "agent_id": "synthetic-fixture",
        "placements": [7, 6, 5, 4, 3, 2, 1, 8],
        "turns": 13,
        "decisions": 49,
        "truncated_combats": 0,
        "turn_limit_end": False,
        "seed": 99841,
        "policy": "baseline",
        "engine_version": "1.1.0",
        "engine_source_hash": ENGINE_HASH,
        "model_sha256": None,
    }


def test_legacy_seat_zero_without_extra_attribution_is_compatible():
    assert validate_integrity(receipt())


def test_correct_rotated_seat_is_accepted():
    row = receipt()
    row.update(seat=3, agent_placement=4)
    assert validate_integrity(row)


def test_correct_rotated_seat_model_digest_is_accepted():
    row = receipt()
    row.update(seat=3, agent_placement=4, policy="model", model_sha256="a" * 64)
    assert validate_integrity(row)


@pytest.mark.parametrize("seat", [-1, 8, True, False, "3", 3.0, None])
def test_invalid_seat_fails_closed(seat):
    row = receipt()
    row.update(seat=seat, agent_placement=4)
    with pytest.raises(ValueError, match="Controlled seat"):
        validate_integrity(row)


@pytest.mark.parametrize("wrong", [7, 3, True, 4.0, "4", None])
def test_wrong_or_invalid_agent_placement_rejected(wrong):
    row = receipt()
    row.update(seat=3, agent_placement=wrong)
    with pytest.raises(ValueError, match="Agent placement"):
        validate_integrity(row)


def test_rotated_seat_must_explicitly_attest_own_placement():
    row = receipt()
    row["seat"] = 3
    with pytest.raises(ValueError, match="requires agent_placement"):
        validate_integrity(row)


def test_explicit_seat_zero_cannot_claim_another_seats_rank():
    row = receipt()
    row.update(seat=0, agent_placement=4)
    with pytest.raises(ValueError, match="Agent placement"):
        validate_integrity(row)


def test_explicit_seat_zero_correct_placement_still_works():
    row = receipt()
    row.update(seat=0, agent_placement=7)
    assert validate_integrity(row)


def test_legacy_receipt_with_optional_correct_placement_still_works():
    row = copy.deepcopy(receipt())
    row["agent_placement"] = 7
    assert validate_integrity(row)
