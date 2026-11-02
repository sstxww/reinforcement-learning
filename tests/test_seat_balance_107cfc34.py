"""Unit checks for isolated seat-sensitivity evaluation; real games run in Actions."""
import pytest
from tavern_ai.seat_balance_107cfc34 import run_seat, summarize

def receipt(seed, seat, rank):
    places = list(range(1, 9))
    places[seat], places[rank - 1] = places[rank - 1], places[seat]
    return {
        "environment": "TavernGym", "completed": True,
        "agent_id": "s-20261102-107cfc34", "seed": seed,
        "controlled_seat": seat, "controlled_placement": rank,
        "placements": places, "turns": 15, "decisions": 8,
        "truncated_combats": 0, "turn_limit_end": False}

def test_paired_statistics_are_seat_indexed():
    report = summarize([
        receipt(21, 0, 2), receipt(21, 1, 6),
        receipt(22, 0, 1), receipt(22, 1, 3)])
    assert report["total_games"] == 4
    assert report["by_seat"]["0"]["mean_placement"] == 1.5
    assert report["by_seat"]["0"]["first_place_rate"] == 0.5
    assert report["by_seat"]["1"]["top4_rate"] == 0.5
    assert report["paired_mean_delta_seat1_minus_seat0"] == 3

def test_incomplete_pair_is_rejected():
    with pytest.raises(ValueError, match="missing seat"):
        summarize([receipt(21, 0, 2)])

def test_duplicate_seat_is_rejected():
    with pytest.raises(ValueError, match="duplicate seat"):
        summarize([receipt(21, 0, 2), receipt(21, 0, 2)])

def test_receipt_seat_mismatch_is_rejected():
    bad = receipt(21, 0, 2)
    bad["controlled_placement"] = 6
    with pytest.raises(ValueError, match="mismatch"):
        summarize([bad])

@pytest.mark.parametrize("seat", [-1, 8])
def test_invalid_seat_fails_without_engine(seat):
    with pytest.raises(ValueError, match="seat must"):
        run_seat(21, "test", seat)
