"""Synthetic negative mutations of original provenance-backed full-game receipts."""
import copy
import json
from pathlib import Path

import pytest

from tavern_ai.paired_buy_gate_023cd77e import compare

ROOT = Path("experiments/s-20261103-4fd17801")
SHA = "a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632"


@pytest.fixture
def receipts():
    b = json.loads((ROOT / "001-baseline-97303.json").read_text())
    m = json.loads((ROOT / "002-source-model-97303.json").read_text())
    return b, m


def test_actual_preexisting_raw_game_evidence_reconciles(receipts):
    baseline, model = receipts
    result = compare(baseline, model, SHA)
    assert result["sample_size"] == 1
    assert result["baseline"]["rank"] == 5
    assert result["raw_model"]["rank"] == 8
    assert result["raw_model"]["buy_chosen"] == 0
    assert result["raw_model"]["buy_legal_decisions"] == 23
    assert result["mean_placement_delta_model_minus_baseline"] == 3
    assert result["result"] == "descriptive_single_seed_only_no_performance_claim"


@pytest.mark.parametrize("mutation", [
    "wrong_seed", "wrong_hash", "assisted", "missing_guard",
    "fake_buy_count", "fake_family_count", "fake_buy_rate",
    "fake_placement", "wrong_engine",
])
def test_edited_receipts_are_rejected(receipts, mutation):
    baseline, original = receipts
    model = copy.deepcopy(original)
    if mutation == "wrong_seed":
        model["seed"] += 1
    elif mutation == "wrong_hash":
        model["model_sha256"] = "f" * 64
    elif mutation == "assisted":
        model["fallback_actions"] = 1
    elif mutation == "missing_guard":
        del model["model_guard_forced_end"]
    elif mutation == "fake_buy_count":
        model["opportunity_summary"]["buy_chosen"] = 12
    elif mutation == "fake_family_count":
        model["opportunity_summary"]["by_action_family"]["other"] += 1
    elif mutation == "fake_buy_rate":
        model["opportunity_summary"]["conditional_buy_rate_given_legal"] = 1.0
    elif mutation == "fake_placement":
        model["placements"][0] = 7
    elif mutation == "wrong_engine":
        model["engine_source_hash"] = "bad-engine"
    with pytest.raises((ValueError, TypeError, KeyError)):
        compare(baseline, model, SHA)
