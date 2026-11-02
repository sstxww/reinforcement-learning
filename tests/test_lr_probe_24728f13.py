"""Regressions for isolated PPO learning-rate study; no mocked games used as evidence."""
import numpy as np
import pytest

from tavern_ai.lr_probe_24728f13 import choose_action, summary


def legal(*actions):
    mask = np.zeros(245, dtype=bool)
    mask[list(actions)] = True
    return mask


def receipt(rank=5, seed=42171):
    return {
        "environment": "TavernGym", "completed": True, "agent_id": "s-20261102-24728f13",
        "seed": seed, "placements": [rank] + [x for x in range(1, 9) if x != rank],
        "turns": 13, "decisions": 80, "truncated_combats": 0,
        "turn_limit_end": False, "guard_forced_ends": 2,
    }


def test_model_action_preserved_before_guard():
    assert choose_action(legal(0, 9), 9, used=39) == (9, False)


def test_guard_forces_only_legal_end_turn():
    assert choose_action(legal(0, 9), None, used=40) == (0, True)


def test_no_guard_when_end_turn_is_not_legal():
    assert choose_action(legal(30, 31), 31, used=40) == (31, False)


@pytest.mark.parametrize("proposal", [None, -1, 246, 8])
def test_illegal_model_proposals_fail_closed(proposal):
    with pytest.raises(ValueError, match="illegal action"):
        choose_action(legal(0, 9), proposal, used=0)


def test_empty_mask_rejected():
    with pytest.raises(ValueError, match="Invalid or empty"):
        choose_action(legal(), 0, used=0)


def test_summary_uses_real_receipt_schema():
    result = summary([receipt(1, 42171), receipt(5, 42172)])
    assert result["games"] == 2
    assert result["mean_rank"] == 3
    assert result["top4_rate"] == 0.5
    assert result["first_rate"] == 0.5
    assert result["guard_forced_ends"] == 4


def test_summary_rejects_duplicate_placements():
    bad = receipt()
    bad["placements"] = [1] * 8
    with pytest.raises(ValueError, match="permutation"):
        summary([bad])
