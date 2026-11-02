"""R002 fresh cap-3 independent policy regressions."""
import importlib.util
from pathlib import Path
import numpy as np

MODULE = Path(__file__).resolve().parents[1] / "research/sessions/s-20261102-221336eb/budget_experiment_r002.py"
spec = importlib.util.spec_from_file_location("budget_experiment_r002_221336eb", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def obs(*legal):
    m = np.zeros(245, dtype=bool)
    m[list(legal)] = True
    return {"action_mask": m}


def test_r002_default_is_three():
    assert mod.CAP == 3
    policy = mod.DecisionBudgetPolicy()
    assert policy.act(obs(0, 8), {"turn": 4, "actions_used": 3}) == 0
    assert policy.interventions == 1


def test_r002_no_end_when_below_cap():
    policy = mod.DecisionBudgetPolicy()
    assert policy.act(obs(0, 8), {"turn": 4, "actions_used": 2}) == 8


def test_r002_forced_choice_still_wins():
    policy = mod.DecisionBudgetPolicy()
    assert policy.act(obs(0, 30), {"turn": 4, "actions_used": 10}) == 30


def test_r002_mask_end_unavailable():
    policy = mod.DecisionBudgetPolicy()
    assert policy.act(obs(8), {"turn": 4, "actions_used": 20}) == 8
