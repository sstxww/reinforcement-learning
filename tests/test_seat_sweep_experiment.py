"""Static gates for R002 seat sweep. Genuine games are only run by Actions."""
import pytest
from tavern_ai.seat_sweep_experiment import (
    compare_seats, run_sweep, summarize_seat,
)


def receipt(seat, seed, controlled_rank):
    places = [x for x in range(1, 9) if x != controlled_rank]
    places.insert(seat, controlled_rank)
    return {
        "environment": "TavernGym",
        "completed": True,
        "agent_id": "test",
        "policy": "baseline",
        "placements": places,
        "controlled_seat": seat,
        "controlled_rank": controlled_rank,
        "turns": 14,
        "decisions": 55,
        "seed": seed,
        "truncated_combats": 0,
        "turn_limit_end": False,
    }


def groups():
    return {seat: [receipt(seat, seed, seat + 1) for seed in (100, 101)]
            for seat in range(8)}


def test_all_seats_aggregate_pairwise_by_seed():
    result = compare_seats(groups())
    assert result["matches"] == 16
    assert result["seed_count"] == 2
    assert result["by_seat"][0]["ranks"] == [1, 1]
    assert result["by_seat"][7]["ranks"] == [8, 8]
    assert result["seat_mean_deltas_vs_seat0"] == list(range(8))
    assert result["seeds_with_nonidentical_seat_ranks"] == 2


def test_single_seat_summary():
    result = summarize_seat([
        receipt(7, 1, 8), receipt(7, 2, 4),
    ])
    assert result["seat"] == 7
    assert result["mean_rank"] == 6
    assert result["first_rate"] == 0
    assert result["top4_rate"] == 0.5


@pytest.mark.parametrize("invalid", [
    {}, {0: [receipt(0, 100, 1)]},
])
def test_incomplete_seat_set_rejected(invalid):
    with pytest.raises(ValueError):
        compare_seats(invalid)


def test_seed_sequence_mismatch_rejected():
    r = groups()
    r[3][1]["seed"] = 99
    with pytest.raises(ValueError, match="matching seed"):
        compare_seats(r)


def test_mixed_seat_summary_rejected():
    with pytest.raises(ValueError, match="one controlled seat"):
        summarize_seat([receipt(0, 1, 1), receipt(1, 2, 2)])


def test_no_seed_rejected_without_engine(tmp_path):
    with pytest.raises(ValueError, match="Independent seeds"):
        run_sweep("test", 10, [], tmp_path, tmp_path / "r.json")
    with pytest.raises(ValueError, match="Independent seeds"):
        run_sweep("test", 10, [11, 11], tmp_path, tmp_path / "r.json")
    with pytest.raises(ValueError, match="Independent seeds"):
        run_sweep("test", 10, [10, 11], tmp_path, tmp_path / "r.json")
