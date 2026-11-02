"""R002 unit tests of telemetry schemas; these do not substitute for real games."""
import pytest

from tavern_ai.action_trace_24728f13 import action_category, summarise


@pytest.mark.parametrize("action,expected", [
    (0, "end_turn"), (3, "upgrade"), (8, "buy_slot"), (15, "buy_slot"),
    (30, "mandatory_choice_range"), (45, "mandatory_choice_range"),
    (46, "hand_play_range"), (125, "hand_play_range"), (196, "other_action"),
])
def test_action_categories(action, expected):
    assert action_category(action) == expected


def r(rank, decisions, end, forced):
    return {
        "environment": "TavernGym", "completed": True, "agent_id": "s-20261102-24728f13",
        "placements": [rank] + [x for x in range(1, 9) if x != rank],
        "turns": 12, "decisions": decisions, "truncated_combats": 0, "turn_limit_end": False,
        "model_chosen_end_turns": end, "guard_forced_ends": forced,
        "action_categories": {"end_turn": end + forced, "buy_slot": 3},
        "max_same_action_streak": 4,
    }


def test_summarise_separates_model_end_and_guard():
    s = summarise([r(8, 20, 8, 0), r(7, 40, 10, 3)])
    assert s["games"] == 2
    assert s["ranks"] == [8, 7]
    assert s["total_actions"] == 60
    assert s["model_chosen_ends"] == 18
    assert s["guard_forced_ends"] == 3
    assert s["action_categories"]["end_turn"] == 21
    assert s["top4_rate"] == 0


def test_empty_records_rejected():
    with pytest.raises(ValueError, match="No real traces"):
        summarise([])
