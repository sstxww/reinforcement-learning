"""Mechanism-safety and metric tests for independent masked BC pilot."""
import numpy as np
import pytest
torch = pytest.importorskip("torch", reason="BC experiment requires optional torch")

from tavern_ai.bc_session_661adf61 import MaskedBC, choose_legal, stack, summarize
from tavern_ai.contract import FEATURES, CARDS, ACTIONS


def fake_sample(action=8):
    f = np.zeros(FEATURES, dtype=np.float32)
    c = np.zeros(CARDS, dtype=np.int32)
    mask = np.zeros(ACTIONS, dtype=bool)
    mask[action] = True
    return f, c, mask, action


def test_mask_is_enforced_when_other_logits_win():
    net = MaskedBC(card_count=12)
    f, c, mask, action = fake_sample(8)
    with torch.no_grad():
        net.actor[-1].bias.fill_(1000.0)
        net.actor[-1].bias[8] = -1000.0
    assert choose_legal(net, f, c, mask) == action


def test_teacher_labels_must_be_legal():
    f, c, mask, _ = fake_sample(8)
    with pytest.raises(ValueError, match="illegal"):
        stack([(f, c, mask, 9)])


def test_zero_valid_actions_rejected_on_labels():
    f, c, mask, _ = fake_sample(8)
    mask[:] = False
    with pytest.raises(ValueError, match="illegal"):
        stack([(f, c, mask, 8)])


def test_distinct_raw_and_guarded_evaluation_metrics():
    raw = {"completed": False, "reason": "raw_turn_budget_exceeded", "policy": "bc_raw"}
    guard = {"completed": True, "placements": [5, 1, 2, 3, 4, 6, 7, 8],
             "forced_end_turns": 3, "policy": "bc_guarded"}
    assert summarize([raw])["completed"] == 0
    assert summarize([raw])["mean_placement"] is None
    assert summarize([guard])["forced_end_turns"] == 3
    assert summarize([guard])["top4_rate"] == 0


def test_train_labels_and_no_hidden_data():
    f, c, m, a = stack([fake_sample(8), fake_sample(9)])
    assert f.shape == (2, FEATURES)
    assert c.shape == (2, CARDS)
    assert m.shape == (2, ACTIONS)
    assert a.tolist() == [8, 9]
