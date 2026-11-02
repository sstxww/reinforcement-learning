"""Unit tests for session-owned mandatory-choice tie-breaker, no fake simulator."""
from pathlib import Path
import runpy

import numpy as np
import pytest

ns = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                        "scripts/choice_tiebreak_s-20261102-9c463177.py"))
Policy = ns["RightmostMandatoryPolicy"]


def obs(*actions):
    mask = np.zeros(245, dtype=bool)
    mask[list(actions)] = True
    return {"action_mask": mask}


def test_rightmost_mandatory_choice_only():
    p = Policy()
    assert p.act(obs(0, 30, 31, 34, 46), {"turn": 4}) == 34
    assert p.multiple_choice_events == 1
    assert p.changed_decisions == 1


def test_single_mandatory_matches_baseline():
    p = Policy()
    assert p.act(obs(0, 32, 39 + 7), {"turn": 1}) == 32
    assert p.multiple_choice_events == 0
    assert p.changed_decisions == 0


def test_nonmandatory_follows_unchanged_baseline():
    p = Policy()
    assert p.act(obs(0, 8, 46), {"turn": 1}) == 46
    assert p.act(obs(0, 9), {"turn": 3}) == 9
    assert p.multiple_choice_events == 0


@pytest.mark.parametrize("actions", [(), (0,)])
def test_mask_validation_and_end_turn(actions):
    p = Policy()
    if not actions:
        with pytest.raises(ValueError):
            p.act(obs(*actions))
    else:
        assert p.act(obs(*actions)) == 0


def test_summary_and_pairing():
    rec = [{"placements": [2], "seed": 1}, {"placements": [8], "seed": 2}]
    stat = ns["summarize"](rec)
    assert stat["games"] == 2
    assert stat["mean_placement"] == 5
    assert stat["top4_rate"] == .5
    assert stat["first_place_rate"] == 0


def test_engine_not_statically_mocked():
    # Real-game driver must call the project canary with its actual engine.
    assert ns["play_baseline"].__code__.co_names.count("run") >= 1
    assert ns["play_candidate"].__code__.co_names.count("run") >= 1
