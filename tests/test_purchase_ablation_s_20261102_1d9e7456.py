"""Isolated purchase action decision tests; no TavernGym installation needed."""
import importlib.util
from pathlib import Path
import numpy as np
import pytest
SCRIPT = Path(__file__).resolve().parents[1] / "research/sessions/s-20261102-1d9e7456/run_purchase_ablation.py"
spec = importlib.util.spec_from_file_location("isolated_purchase_ablation", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def obs(*legal):
    mask = np.zeros(245, dtype=bool)
    mask[list(legal)] = True
    return {"action_mask": mask}

def test_rightmost_changes_only_buy_choice():
    assert module.PurchasePolicy("baseline", 38100).act(obs(0, 8, 9, 12)) == 8
    assert module.PurchasePolicy("rightmost", 38100).act(obs(0, 8, 9, 12)) == 12
    assert module.PurchasePolicy("rightmost", 38100).act(obs(0, 8, 30)) == 30

def test_seeded_uniform_reproduces_and_respects_mask():
    p = module.PurchasePolicy("uniform", 38100)
    q = module.PurchasePolicy("uniform", 38100)
    actions = [p.act(obs(0, 8, 9, 12)) for _ in range(30)]
    assert actions == [q.act(obs(0, 8, 9, 12)) for _ in range(30)]
    assert set(actions) <= {8, 9, 12}
    assert p.choice_opportunities == 30

def test_end_turn_and_fail_closed():
    assert module.PurchasePolicy("uniform", 1).act(obs(0)) == 0
    with pytest.raises(ValueError):
        module.PurchasePolicy("unrecognized", 1)
    with pytest.raises(ValueError):
        module.PurchasePolicy("uniform", 1).act(obs())
