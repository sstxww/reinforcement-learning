import pytest
from tavern_ai.entropy_probe import VARIANTS, aggregate


def receipt(seed, rank):
    return {"environment": "TavernGym", "completed": True,
            "agent_id": "unit-test", "seed": seed,
            "turns": 10, "decisions": 11,
            "placements": [rank] + [x for x in range(1, 9) if x != rank],
            "truncated_combats": 0, "turn_limit_end": False}


def test_aggregate():
    m = aggregate([receipt(1, 1), receipt(2, 8)])
    assert m["mean_placement"] == 4.5
    assert m["top4_rate"] == 0.5
    assert m["first_place_rate"] == 0.5
    assert m["seeds"] == [1, 2]


def test_reject_invalid():
    with pytest.raises(ValueError):
        aggregate([])
    bad = receipt(1, 3)
    bad["turn_limit_end"] = True
    with pytest.raises(ValueError):
        aggregate([bad])


def test_variant_parameters():
    assert VARIANTS == {"zero": 0.0, "regularized": 0.02}
