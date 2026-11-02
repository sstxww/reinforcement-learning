import numpy as np
import pytest
from tavern_ai.mechanics_probe_a881710a import (
    ACTIONS, ACTION_RANGES, EXPECTED_COLS, KINDS, action_family, decode_row,
)


def test_action_family_is_partition_and_semantic_bounds():
    assert sum(hi - lo for _, lo, hi in ACTION_RANGES) == ACTIONS
    assert [a for _, lo, hi in ACTION_RANGES for a in range(lo, hi)] == list(range(ACTIONS))
    assert action_family(0) == "end_turn"
    assert action_family(8) == "buy"
    assert action_family(45) == "choose"
    assert action_family(46) == "play"
    assert action_family(125) == "play"
    assert action_family(126) == "magnetize"
    assert action_family(196) == "move"
    with pytest.raises(ValueError):
        action_family(245)


def test_decode_static_row_non_leaky_fields():
    row = np.zeros(EXPECTED_COLS, dtype=np.float32)
    row[0] = 1
    row[10:15] = [3, 5, 6, 3, 0]
    row[15] = 1
    row[37 + 1] = 1
    row[49] = 1
    row[61] = 1
    c = decode_row(13, ("TEST_01", "Test", "测试", 3), row)
    assert c["kind"] == KINDS[0]
    assert c["races"] == ["BEAST"]
    assert c["keywords"] == ["DIVINE_SHIELD"]
    assert c["printed_mechanics"] == ["BATTLECRY"]
    assert c["static_pool_flags"] == ["minion"]
    assert c["effect_script_verified"] is False


def test_decode_detects_mismatch_and_corruption():
    row = np.zeros(EXPECTED_COLS, dtype=np.float32)
    row[0] = 1
    row[10] = 2
    with pytest.raises(ValueError, match="tier"):
        decode_row(1, ("X", "", "", 3), row)
    row[10] = 3
    row[1] = 1
    with pytest.raises(ValueError, match="one-hot"):
        decode_row(1, ("X", "", "", 3), row)
    row[1] = 0
    row[37] = 2
    with pytest.raises(ValueError, match="binary"):
        decode_row(1, ("X", "", "", 3), row)
