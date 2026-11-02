"""Pure regression tests; mock receipts are NOT genuine game evidence."""
from __future__ import annotations

from copy import deepcopy

import pytest

from tavern_ai.contract import ENGINE_HASH
from tavern_ai.v2_opportunity_s_90e24c7b import (
    MAX_PER_TURN, V2_SHA256, action_family, aggregate, load_verified_model,
)


@pytest.mark.parametrize("idx,family", [
    (0, "end"), (1, "refresh"), (2, "freeze"), (3, "upgrade"),
    (8, "buy"), (15, "buy"), (16, "sell"), (22, "sell"),
    (30, "choose"), (45, "choose"), (46, "play"), (125, "play"),
    (126, "magnetize"), (195, "magnetize"), (196, "move"), (244, "move"),
])
def test_pinned_action_families(idx, family):
    assert action_family(idx) == family


def test_illegal_action_family_rejected():
    for i in (-1, 245, 999):
        with pytest.raises(ValueError):
            action_family(i)
    assert MAX_PER_TURN == 75


def synthetic_receipt(rank=8, buy_legal=4, buys=0, guard=0):
    """Explicit test fixture only, never saved as game output."""
    return {
        "environment": "TavernGym", "completed": True, "agent_id": "fixture",
        "engine_version": "1.1.0", "engine_source_hash": ENGINE_HASH,
        "policy": "model", "model_sha256": V2_SHA256,
        "seed": 1, "turns": 15, "decisions": 20,
        "placements": [rank] + [p for p in range(1, 9) if p != rank],
        "truncated_combats": 0, "turn_limit_end": False,
        "legal_buy_decisions": buy_legal, "legal_buy_turn_count": 2,
        "buy_actions": buys, "end_with_buy_available": 2,
        "guard_forced_ends": guard,
    }


def test_aggregation_distinguishes_legal_opportunity_from_action():
    first = synthetic_receipt(rank=8, buy_legal=8, buys=0, guard=1)
    second = synthetic_receipt(rank=7, buy_legal=4, buys=2, guard=0)
    result = aggregate([first, second])
    assert result["games"] == 2
    assert result["mean_rank"] == 7.5
    assert result["selected_buy_actions"] == 2
    assert result["buy_legal_decisions"] == 12
    assert result["buy_per_legal_decision"] == pytest.approx(2 / 12)
    assert result["guard_forced_ends"] == 1
    assert result["top4_rate"] == 0


def test_zero_legal_opportunities_yields_null_rate():
    data = aggregate([synthetic_receipt(buy_legal=0, buys=0)])
    assert data["buy_per_legal_decision"] is None


def test_nonpermutation_rejected():
    bad = synthetic_receipt()
    bad["placements"] = [8] * 8
    with pytest.raises(ValueError, match="permutation"):
        aggregate([bad])


def test_wrong_release_hash_fails_before_model_deserialization(tmp_path):
    path = tmp_path / "model.zip"
    path.write_bytes(b"untrusted or corrupt model payload")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        load_verified_model(path)
