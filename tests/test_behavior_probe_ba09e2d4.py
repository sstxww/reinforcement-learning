"""Unit tests for model-independent legal-opportunity telemetry."""
import numpy as np
import pytest

from tavern_ai.behavior_probe_ba09e2d4 import FAMILIES, OpportunityTrace, family
from tavern_ai.contract import ACTIONS


def test_action_family_partition_is_exact():
    assert FAMILIES[0][:] == ("end_turn", 0, 1)
    assert sum(hi - lo for _, lo, hi in FAMILIES) == ACTIONS
    assert [family(i) for i in range(ACTIONS)].count("buy") == 8
    assert family(0) == "end_turn"
    assert family(3) == "upgrade"


def test_legal_buy_offer_vs_actual_buy():
    probe = OpportunityTrace()
    legal = np.zeros(ACTIONS, dtype=bool)
    legal[[0, 8, 9]] = True
    probe.record(3, legal, 0)
    probe.record(3, legal, 8)
    report = probe.report()
    assert report["buy_legal_decisions"] == 2
    assert report["buy_opportunity_turns"] == 1
    assert report["actual_buys"] == 1
    assert report["end_with_legal_buy"] == 1
    assert report["max_consecutive_same_action_in_turn"] == 1


def test_no_buy_mask_exonerates_missing_buys():
    probe = OpportunityTrace()
    legal = np.zeros(ACTIONS, dtype=bool)
    legal[0] = True
    probe.record(4, legal, 0)
    assert probe.report()["buy_legal_decisions"] == 0
    assert probe.report()["end_with_legal_buy"] == 0


def test_repetition_and_illegal_action():
    probe = OpportunityTrace()
    mask = np.zeros(ACTIONS, dtype=bool)
    mask[1] = True
    for _ in range(3):
        probe.record(5, mask, 1)
    assert probe.report()["max_consecutive_same_action_in_turn"] == 3
    with pytest.raises(ValueError, match="Illegal"):
        probe.record(5, mask, 8)
    with pytest.raises(ValueError):
        family(245)
