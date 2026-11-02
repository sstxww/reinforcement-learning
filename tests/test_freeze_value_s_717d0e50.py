import numpy as np
import pytest
from tavern_ai.freeze_value_s_717d0e50 import select_action, shop_start, shop_is_valuable, verify_public_observation_layout

LAYOUT = {"GLOBAL_F": 60, "N_QUESTS": 3, "QUEST_F": 2, "PENDING_KINDS": 9,
          "N_BOARD": 7, "MINION_F": 19, "N_HAND": 10, "ITEM_F": 28, "N_SHOP": 8}


def make_obs():
    f = np.zeros(4017, dtype=np.float32)
    f[10] = 2 / 6
    start = shop_start(LAYOUT)
    f[start] = 1
    f[start + 1] = 1
    f[start + 10] = 0.3
    f[start + 11] = 0.3
    f[start + 13] = 2 / 6
    return f


def mask(*allowed):
    m = np.zeros(245, dtype=bool)
    m[list(allowed)] = True
    return m


def test_value_gate_decodes_public_shop_features():
    f = make_obs()
    assert shop_is_valuable(f, LAYOUT)
    f[15] = 1
    assert not shop_is_valuable(f, LAYOUT)
    f[15] = 0
    f[shop_start(LAYOUT) + 13] = 1 / 6
    assert not shop_is_valuable(f, LAYOUT)


def test_conservative_freeze_only_when_valuable_and_unfrozen():
    m = mask(0, 2)
    f = make_obs()
    assert select_action(f, m, 6, 5, False, "quality-freeze", LAYOUT) == 2
    f[15] = 1
    assert select_action(f, m, 6, 5, False, "quality-freeze", LAYOUT) == 0
    assert select_action(f, m, 6, 5, False, "blind-freeze", LAYOUT) == 2
    assert select_action(f, m, 6, 5, False, "baseline", LAYOUT) == 0


def test_guard_masks_and_pending_choices():
    f = make_obs()
    m = mask(0, 2)
    assert select_action(f, m, 6, 85, False, "quality-freeze", LAYOUT) == 0
    assert select_action(f, m, 6, 4, True, "quality-freeze", LAYOUT) == 0
    assert select_action(f, m, 10, 5, False, "quality-freeze", LAYOUT) == 0
    assert select_action(f, mask(30), 6, 5, False, "quality-freeze", LAYOUT) == 30
    assert select_action(f, mask(0, 1, 2), 6, 5, False, "quality-freeze", LAYOUT) == 0
    assert select_action(f, mask(0, 2, 8), 6, 5, False, "quality-freeze", LAYOUT) == 8
    with pytest.raises(ValueError):
        select_action(f, m, 6, 5, False, "unknown", LAYOUT)


def test_dual_observation_contract_and_shop_offsets():
    """Patched TavernGym reports both 3227/124 V1 and 4017/447 V2 observations."""
    layout = dict(LAYOUT, OBS_FLOATS=3227, OBS_CARDS=124,
                  OBS2_FLOATS=4017, OBS2_CARDS=447, N_ACTIONS=245)
    # The documented legacy observation has 3227 float features;
    # the public shop starts after global, quests, pending, board and hand.
    assert shop_start(layout) == 685
    verify_public_observation_layout(layout)
    with pytest.raises(RuntimeError, match="observe2"):
        verify_public_observation_layout(dict(layout, OBS2_FLOATS=3227))
    with pytest.raises(RuntimeError, match="legacy public shop"):
        verify_public_observation_layout(dict(layout, OBS_FLOATS=4017))
