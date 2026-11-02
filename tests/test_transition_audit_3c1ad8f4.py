"""Pure regression tests for the independent public state-transition telemetry."""
import numpy as np
import pytest

from tavern_ai.transition_audit_3c1ad8f4 import TransitionCounts, family
from tavern_ai.contract import ACTIONS, CARDS, FEATURES


def state():
    return np.zeros(FEATURES, dtype=np.float32), np.zeros(CARDS, dtype=np.int32)


def legal(*actions):
    m = np.zeros(ACTIONS, dtype=bool)
    m[list(actions)] = True
    return m


def test_refresh_unchanged_public_projection_is_not_claimed_as_internal_noop():
    t = TransitionCounts()
    f, c = state()
    t.record(turn=1, mask=legal(1, 8), action=1,
             before_f=f, before_c=c, after_f=f.copy(), after_c=c.copy(), same_turn=True)
    row = t.summary()["action_families"]["refresh"]
    assert row["public_observation_unchanged"] == 1
    assert row["same_turn_comparisons"] == 1
    assert t.summary()["turns"]["1"]["buy_legal_exposures"] == 1
    assert "DOES NOT prove" in t.summary()["limitations"][0]


def test_freeze_detects_float_and_card_delta_without_leaking_raw_observation():
    t = TransitionCounts()
    f, c = state()
    af, ac = f.copy(), c.copy()
    af[123] = 2.0
    ac[42] = 7
    t.record(turn=5, mask=legal(2), action=2,
             before_f=f, before_c=c, after_f=af, after_c=ac, same_turn=True)
    out = t.summary()
    row = out["action_families"]["freeze"]
    assert row["public_observation_changed"] == 1
    assert row["features_changed_total"] == row["cards_changed_total"] == 1
    assert out["examples"][0]["features_changed"] == 1
    assert "features" not in out["examples"][0]


def test_repeated_legal_exposures_are_not_independent_buy_offers():
    t = TransitionCounts()
    f, c = state()
    for _ in range(3):
        t.record(turn=2, mask=legal(0, 8), action=0, before_f=f, before_c=c)
    out = t.summary()
    assert out["decisions"] == 3
    assert out["turns"]["2"]["buy_legal_exposures"] == 3
    assert out["action_families"]["end"]["end_with_legal_buy"] == 3
    assert len(out["turns"]) == 1


def test_guard_is_explicit_and_does_not_count_as_model_chosen_end():
    t = TransitionCounts()
    f, c = state()
    t.record(turn=3, mask=legal(0), action=0, before_f=f, before_c=c, forced=True)
    assert t.summary()["guard_forced_ends"] == 1
    assert t.summary()["action_families"]["end"]["guard_forced"] == 1


@pytest.mark.parametrize("action,mask", [
    (8, legal(0)),
    (0, legal(8)),
    (245, legal(0)),
])
def test_fail_closed_on_illegal_policy_action(action, mask):
    t = TransitionCounts()
    f, c = state()
    with pytest.raises(ValueError, match="Illegal action"):
        t.record(turn=1, mask=mask, action=action, before_f=f, before_c=c)


def test_same_turn_requires_post_observation_and_guard_only_end():
    t = TransitionCounts()
    f, c = state()
    with pytest.raises(ValueError, match="Missing same-turn"):
        t.record(turn=2, mask=legal(1), action=1,
                 before_f=f, before_c=c, same_turn=True)
    with pytest.raises(ValueError, match="Guard can only"):
        t.record(turn=2, mask=legal(1), action=1,
                 before_f=f, before_c=c, forced=True)
    assert family(1) == "refresh"
    assert family(2) == "freeze"
    assert family(8) == "buy"
    assert family(197) == "move"
