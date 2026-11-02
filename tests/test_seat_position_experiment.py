"""Unit gates for the separate seat-position audit. Real games run in Actions."""
import pytest

from tavern_ai.seat_position_experiment import (
    play, summarize, verify_controlled_receipt, run_experiment,
)


def receipt(seat=4, ranks=None, seed=1):
    ranks = ranks or [1, 2, 3, 4, 5, 6, 7, 8]
    return {
        "environment": "TavernGym", "completed": True,
        "agent_id": "test", "policy": "baseline",
        "placements": ranks, "controlled_seat": seat,
        "controlled_rank": ranks[seat], "turns": 15,
        "decisions": 43, "seed": seed,
        "truncated_combats": 0, "turn_limit_end": False,
    }


@pytest.mark.parametrize("seat", list(range(8)))
def test_all_controlled_seats_accepted(seat):
    assert verify_controlled_receipt(receipt(seat=seat))


@pytest.mark.parametrize("seat", [-1, 8, True, 1.5])
def test_invalid_seat_rejected(seat):
    x = receipt()
    x["controlled_seat"] = seat
    with pytest.raises(ValueError, match="Controlled seat"):
        verify_controlled_receipt(x)


def test_controlled_rank_must_match_actual_seat():
    x = receipt(seat=4)
    x["controlled_rank"] = x["placements"][0]
    with pytest.raises(ValueError, match="Controlled rank"):
        verify_controlled_receipt(x)


def test_nonpermutation_rejected():
    x = receipt()
    x["placements"][4] = x["placements"][5]
    x["controlled_rank"] = x["placements"][4]
    with pytest.raises(ValueError, match="permutation"):
        verify_controlled_receipt(x)


def test_eight_player_rank_summary_reads_selected_seat_not_first():
    a = receipt(seat=4, seed=101)
    b = receipt(seat=4, ranks=[8, 7, 6, 5, 1, 2, 3, 4], seed=102)
    actual = summarize([a, b])
    assert actual["ranks"] == [5, 1]
    assert actual["mean_placement"] == 3
    assert actual["top4_rate"] == 0.5
    assert actual["first_place_rate"] == 0.5


def test_no_empty_summary():
    with pytest.raises(ValueError):
        summarize([])


def test_bad_play_arguments_fail_before_importing_engine():
    with pytest.raises(ValueError):
        play(-1, "test", 4)
    with pytest.raises(ValueError):
        play(1, "test", 8)
    with pytest.raises(ValueError):
        play(1, "a/b", 4)


def test_pair_seed_guard_before_any_game(tmp_path):
    with pytest.raises(ValueError, match="distinct"):
        run_experiment("test", 1, [2, 2], tmp_path, tmp_path / "report.json")
