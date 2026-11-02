import pytest

from tavern_ai.seat_rotation import summarize, validate_grid


def test_grid_validates_seats_and_game_budget():
    validate_grid([41021, 41022], [0, 3, 6])
    with pytest.raises(ValueError, match="Seats"):
        validate_grid([1], [8])
    with pytest.raises(ValueError, match="unique"):
        validate_grid([1, 1], [0])
    with pytest.raises(ValueError, match="unique"):
        validate_grid([1], [0, 0])
    with pytest.raises(ValueError, match="1..12"):
        validate_grid([1, 2], list(range(7)))


def test_summarize_indexes_controlled_seat_not_seat_zero():
    rows = [
        {"seed": 111, "seat": 0, "placements": [4, 5, 6, 1, 2, 3, 7, 8]},
        {"seed": 111, "seat": 3, "placements": [2, 3, 4, 8, 1, 5, 6, 7]},
        {"seed": 112, "seat": 0, "placements": [2, 1, 3, 4, 5, 6, 7, 8]},
        {"seed": 112, "seat": 3, "placements": [8, 7, 6, 1, 2, 3, 4, 5]},
    ]
    r = summarize(rows)
    assert r["games"] == 4
    assert r["by_seat"]["0"]["mean_placement"] == 3
    assert r["by_seat"]["0"]["top4_rate"] == 1
    assert r["by_seat"]["3"]["mean_placement"] == 4.5
    assert r["by_seat"]["3"]["first_place_rate"] == 0.5
    assert r["by_seat"]["3"]["seeds"] == [111, 112]


def test_zero_records_fail_fast():
    with pytest.raises(ValueError, match="zero"):
        summarize([])
