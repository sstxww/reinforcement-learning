import numpy as np
import pytest
from tavern_ai.upgrade_frequency_s_20261102_9c034841 import TracedBuyPolicy, real_match

def obs(*ids):
    mask = np.zeros(245, dtype=bool)
    mask[list(ids)] = True
    return {"action_mask": mask}

def test_once_buy_at_first_decision():
    p = TracedBuyPolicy(1)
    assert p.act(obs(0, 3, 8), {"turn": 2, "actions_used": 0}) == 8
    assert p.upgrade_to_buy_overrides == 1

def test_one_vs_three_differ_after_one_action():
    once, three = TracedBuyPolicy(1), TracedBuyPolicy(3)
    context = {"turn": 5, "actions_used": 1}
    assert once.act(obs(0, 3, 8), context) == 3
    assert three.act(obs(0, 3, 8), context) == 8
    assert once.upgrade_to_buy_overrides == 0
    assert three.upgrade_to_buy_overrides == 1

def test_three_stops_after_three():
    p = TracedBuyPolicy(3)
    assert p.act(obs(0, 3, 8), {"turn": 7, "actions_used": 3}) == 3

def test_off_turn_preserves_original_buy_priority():
    assert TracedBuyPolicy(1).act(obs(0, 3, 8), {"turn": 4, "actions_used": 0}) == 8

def test_discover_and_play_priority_preserved():
    p = TracedBuyPolicy(1)
    assert p.act(obs(0, 3, 8, 30), {"turn": 2, "actions_used": 0}) == 30
    assert p.act(obs(0, 3, 8, 46), {"turn": 2, "actions_used": 0}) == 46
    assert p.upgrade_to_buy_overrides == 0

def test_no_buy_preserves_upgrade():
    assert TracedBuyPolicy(1).act(obs(0, 3), {"turn": 2, "actions_used": 0}) == 3

@pytest.mark.parametrize("bad", [0, 2, 4, -1])
def test_max_initial_actions_rejects_other_values(bad):
    with pytest.raises(ValueError):
        TracedBuyPolicy(bad)

def test_bad_action_mask_rejected():
    with pytest.raises(ValueError, match="245"):
        TracedBuyPolicy(1).act({"action_mask": np.ones(244, dtype=bool)})

def test_unknown_arm_rejected_before_engine_import():
    with pytest.raises(ValueError, match="Unknown arm"):
        real_match(49201, "unknown")
