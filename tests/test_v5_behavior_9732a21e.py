import numpy as np
import pytest

from tavern_ai.v5_behavior_9732a21e import ACTION_RANGES, TraceCounts, action_family


def mask(*indices):
    v = np.zeros(245, dtype=bool)
    v[list(indices)] = True
    return v


def test_action_partition_is_complete_and_unambiguous():
    indices = [n for _, lo, hi in ACTION_RANGES for n in range(lo, hi)]
    assert indices == list(range(245))
    assert action_family(0) == "end_turn"
    assert action_family(8) == "buy"
    assert action_family(15) == "buy"
    assert action_family(46) == "play"
    assert action_family(244) == "move"


def test_buy_legal_end_is_counted_without_calling_it_an_illegal_action():
    stats = TraceCounts()
    stats.record(turn=3, action=0, mask=mask(0, 8, 9), gold=5.0, digest="x")
    out = stats.to_json()
    assert out["legal_buy_decisions"] == 1
    assert out["legal_buy_end_turns"] == 1
    assert out["gold_positive_legal_buy_ends"] == 1
    assert out["legal_buy_nonbuy_choices"] == 1
    assert out["chosen_action_families"] == {"end_turn": 1}
    assert out["legal_action_family_decisions"]["buy"] == 1


def test_same_public_observation_diagnosis_not_mislabeled_a_finished_game():
    stats = TraceCounts()
    legal = mask(0, 1)
    stats.record(3, 1, legal, 0.0, "same")
    stats.record(3, 1, legal, 0.0, "same")
    out = stats.to_json()
    assert out["same_public_observation_transitions"] == 1
    assert out["max_same_action_streak"] == 2
    assert out["max_same_public_observation_streak"] == 2
    assert out["legal_buy_decisions"] == 0
    stats.record(4, 0, legal, 0.0, "same")
    assert stats.to_json()["same_public_observation_transitions"] == 1


def test_mask_mismatch_and_bad_action_are_rejected():
    stats = TraceCounts()
    with pytest.raises(ValueError):
        stats.record(1, 8, mask(0), 3.0, "x")
    for action in (-1, 245, True):
        with pytest.raises(ValueError):
            action_family(action)


def test_buy_selected_when_legal_has_zero_missed_buy_counter():
    stats = TraceCounts()
    stats.record(5, 8, mask(0, 8), 3.0, "buy-1")
    assert stats.to_json()["legal_buy_nonbuy_choices"] == 0
    assert stats.to_json()["legal_buy_end_turns"] == 0
