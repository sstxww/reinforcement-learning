import numpy as np
import pytest
from tavern_ai.refresh_ablation import RefreshOncePolicy, summarize

def obs(*legal):
    mask = np.zeros(245, dtype=bool)
    mask[list(legal)] = True
    return {"action_mask": mask}

def test_one_refresh_then_end_even_if_still_legal():
    policy = RefreshOncePolicy()
    assert policy.act(obs(0, 1), turn=5, actions_used=2) == 1
    assert policy.act(obs(0, 1), turn=5, actions_used=3) == 0
    assert policy.total_refreshes == 1
    assert policy.act(obs(0, 1), turn=6, actions_used=1) == 1

def test_mandatory_choice_or_buy_always_precedes_refresh():
    policy = RefreshOncePolicy()
    assert policy.act(obs(0, 1, 30), turn=5, actions_used=0) == 30
    assert policy.act(obs(0, 1, 8), turn=5, actions_used=1) == 8
    assert policy.total_refreshes == 0

def test_too_early_and_action_budget_respected():
    policy = RefreshOncePolicy()
    assert policy.act(obs(0, 1), turn=2, actions_used=3) == 0
    assert policy.act(obs(0, 1), turn=6, actions_used=85) == 0

def test_disabled_cap_exactly_matches_baseline_for_end_case():
    policy = RefreshOncePolicy(max_refreshes_per_turn=0)
    assert policy.act(obs(0, 1), turn=5, actions_used=1) == 0
    with pytest.raises(ValueError, match="cap"):
        RefreshOncePolicy(max_refreshes_per_turn=-1)

def test_empty_action_mask_is_rejected():
    with pytest.raises(ValueError, match="mask"):
        RefreshOncePolicy().act(obs(), turn=5, actions_used=1)

def test_summary_calculates_rates_on_recorded_placements():
    rows = [{"seed": 100, "placements": [1,2,3,4,5,6,7,8]},
            {"seed": 101, "placements": [8,1,2,3,4,5,6,7]}]
    actual = summarize(rows)
    assert actual["mean_placement"] == 4.5
    assert actual["first_place_rate"] == 0.5
    assert actual["top4_rate"] == 0.5
    with pytest.raises(ValueError):
        summarize([])
