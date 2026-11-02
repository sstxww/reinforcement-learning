"""Unit contract tests; the actual matches run only on genuine TavernGym."""
import numpy as np
import pytest
from tavern_ai.baseline import BaselinePolicy
from tavern_ai.discover_slot_ablation_s_b34940b0 import (
    LastDiscoverPolicy, POLICY_VERSION, play, experiment,
)


def observation(*legal: int) -> dict:
    mask = np.zeros(245, dtype=bool)
    mask[list(legal)] = True
    return {"action_mask": mask}


def test_last_choice_changes_only_multi_option_discovery():
    obs = observation(0, 30, 32, 40, 8)
    assert BaselinePolicy().act(obs) == 30
    assert LastDiscoverPolicy().act(obs) == 40


def test_unrelated_buy_and_play_logic_is_unchanged():
    for obs in (observation(0, 8, 46), observation(0, 9), observation(0)):
        assert LastDiscoverPolicy().act(obs) == BaselinePolicy().act(obs)


def test_single_discover_option_is_identical():
    obs = observation(0, 35, 9)
    assert LastDiscoverPolicy().act(obs) == BaselinePolicy().act(obs) == 35


def test_rejects_empty_mask_and_bad_shape():
    with pytest.raises(ValueError):
        LastDiscoverPolicy().act(observation())
    with pytest.raises(ValueError):
        LastDiscoverPolicy().act({"action_mask": np.ones(10, dtype=bool)})


def test_rejects_unknown_policy_without_engine_import():
    with pytest.raises(ValueError, match="Unknown policy"):
        play(1, "unrecognized")


def test_rejects_unbounded_game_budget(tmp_path):
    with pytest.raises(ValueError, match="1..12"):
        experiment(1, 13, tmp_path / "receipts", tmp_path / "report.json")
