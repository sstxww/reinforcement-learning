"""Regression tests for the session-local capped baseline policy."""
import numpy as np
import pytest
from pathlib import Path
import importlib.util

MODULE = Path(__file__).resolve().parents[1] / "research/sessions/s-20261102-221336eb/budget_experiment.py"
spec = importlib.util.spec_from_file_location("budget_experiment_221336eb", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def obs(*legal):
    mask = np.zeros(245, dtype=bool)
    mask[list(legal)] = True
    return {"action_mask": mask}


def test_candidate_ends_turn_after_cap():
    policy = mod.DecisionBudgetPolicy(limit=6)
    assert policy.act(obs(0, 8), {"turn": 3, "actions_used": 6}) == 0
    assert policy.interventions == 1


def test_candidate_matches_baseline_before_cap():
    policy = mod.DecisionBudgetPolicy(limit=6)
    assert policy.act(obs(0, 8), {"turn": 3, "actions_used": 5}) == 8
    assert policy.interventions == 0


def test_candidate_preserves_mandatory_choice():
    policy = mod.DecisionBudgetPolicy(limit=6)
    assert policy.act(obs(0, 30), {"turn": 3, "actions_used": 30}) == 30
    assert policy.interventions == 0


def test_candidate_obeys_mask_if_end_unavailable():
    policy = mod.DecisionBudgetPolicy(limit=6)
    assert policy.act(obs(8), {"turn": 3, "actions_used": 30}) == 8
    assert policy.interventions == 0


def test_candidate_rejects_invalid_limit():
    with pytest.raises(ValueError):
        mod.DecisionBudgetPolicy(limit=0)
