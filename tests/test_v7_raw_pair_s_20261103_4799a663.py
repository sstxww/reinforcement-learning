"""Synthetic integrity regressions: no fake eighth place for failed raw games."""
import pytest
from scripts.v7_raw_pair_s_20261103_4799a663 import require_complete

SEED = 99687
HASH = "a" * 64

def receipt(policy="model"):
    return {"seed": SEED, "policy": policy, "completed": True,
            "turn_limit_end": False, "truncated_combats": 0,
            "fallback_actions": 0, "guard_forced_ends": 0,
            "placements": [8, 4, 1, 5, 2, 3, 6, 7],
            "model_sha256": HASH if policy == "model" else None}

def test_clean_raw_model_and_baseline_receipts():
    require_complete(receipt(), seed=SEED, policy="model", expected_model_sha=HASH)
    require_complete(receipt("baseline"), seed=SEED, policy="baseline")

@pytest.mark.parametrize("key,value", [
    ("completed", False), ("turn_limit_end", True),
    ("truncated_combats", 1), ("fallback_actions", 1),
    ("guard_forced_ends", 1), ("placements", [8] * 8),
    ("seed", SEED + 1), ("policy", "baseline"),
    ("model_sha256", "b" * 64)])
def test_reject_fake_completed_raw_game(key, value):
    bad = receipt()
    bad[key] = value
    with pytest.raises(ValueError):
        require_complete(bad, seed=SEED, policy="model", expected_model_sha=HASH)

def test_unfinished_game_cannot_be_recorded_as_eighth():
    bad = receipt()
    bad.update(completed=False, placements=None)
    with pytest.raises(ValueError, match="naturally completed"):
        require_complete(bad, seed=SEED, policy="model", expected_model_sha=HASH)
