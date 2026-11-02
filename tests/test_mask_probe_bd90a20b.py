"""Dependency-light unit tests; real engine is exercised in the unique workflow."""
import numpy as np
import pytest
from tavern_ai.contract import ACTIONS, CARDS, FEATURES
from tavern_ai.mask_probe_bd90a20b import MaskTrace, bucket


@pytest.mark.parametrize("action,label", [
    (0, "000-007"), (8, "008-015"), (30, "030-045"),
    (46, "046-125"), (126, "126-195"), (244, "196-244")
])
def test_action_buckets(action, label):
    assert bucket(action) == label


def test_bucket_out_of_range():
    with pytest.raises(ValueError):
        bucket(ACTIONS)


def test_repeated_observation_detection():
    trace = MaskTrace()
    m = np.zeros(ACTIONS, dtype=bool)
    m[0] = m[8] = True
    f, c = bytes(FEATURES * 4), bytes(CARDS * 4)
    trace.record(1, f, c, m, 8)
    trace.record(1, f, c, m, 0)
    trace.record(2, f, c, m, 0)
    s = trace.summarize()
    assert s["mask_checks"] == 3
    assert s["minimum_legal_actions"] == 2
    assert s["revisited_observations"] == 1
    assert s["max_identical_observation_visits"] == 2
    assert s["max_own_decisions_in_turn"] == 2
    assert s["action_buckets"] == {"000-007": 2, "008-015": 1}


def test_rejects_illegal_or_empty_masks():
    f, c = bytes(FEATURES * 4), bytes(CARDS * 4)
    trace = MaskTrace()
    m = np.zeros(ACTIONS, dtype=bool)
    with pytest.raises(ValueError, match="mask"):
        trace.record(1, f, c, m, 0)
    m[0] = True
    with pytest.raises(ValueError, match="illegal"):
        trace.record(1, f, c, m, 8)
    with pytest.raises(ValueError, match="layout"):
        trace.record(1, b"", c, m, 0)
