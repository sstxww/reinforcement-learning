"""Regression guards for genuine P2 evidence, no fabricated game data."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from tavern_ai.guarded_evidence_gate_e8355ba3 import audit

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "reports/s-20261102-ba09e2d4/002-action-opportunities.json"
GUARDED = ROOT / "reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json"


@pytest.fixture
def evidence():
    return json.loads(RAW.read_text()), json.loads(GUARDED.read_text())


def test_real_reports_reconcile_without_strength_claim(evidence):
    result = audit(*evidence)
    assert result["raw_model_completed"] is False
    assert result["raw_decisions"] == 6000
    assert result["raw_hero_power_cancel_actions"] == 5955
    assert result["raw_buy_legal_decisions"] == 10
    assert result["raw_buys"] == 0
    assert result["raw_game_rank"] is None
    assert result["guarded_games_completed"] == 2
    assert result["guarded_ranks"] == [8, 8]
    assert result["paired_baseline_ranks"] == [5, 7]
    assert result["paired_mean_rank_delta"] == 2
    assert result["guard_interventions"] == 4
    assert result["champion_promotable"] is False


@pytest.mark.parametrize("field,value", [
    ("complete_eight_seat_game", True),
    ("final_controlled_placement", 8),
    ("safety_fallback_count", 1),
    ("actual_buys", 11),
    ("decisions", 5999),
    ("source_model_sha256", "0" * 64),
])
def test_raw_corruption_rejected(evidence, field, value):
    raw, paired = deepcopy(evidence)
    raw[field] = value
    with pytest.raises(ValueError):
        audit(raw, paired)


@pytest.mark.parametrize("mutation", [
    lambda p: p.update(champion_eligible=True),
    lambda p: p["guarded_model"].update(completed=[True, False]),
    lambda p: p["guarded_model"].update(seeds=[87102, 87102]),
    lambda p: p["baseline"].update(seeds=[87103, 87102]),
    lambda p: p.update(paired_deltas=[0, 0]),
    lambda p: p["guarded_model"].update(guard_interventions=[239, 0]),
    lambda p: p.update(engine_source_hash="incorrect"),
])
def test_guarded_corruption_rejected(evidence, mutation):
    raw, paired = deepcopy(evidence)
    mutation(paired)
    with pytest.raises(ValueError):
        audit(raw, paired)
