"""Synthetic unit fixtures ONLY; never count these as TavernGym match receipts."""
import json

import pytest

from tavern_ai.paired_evidence_s71136659 import compare


def _receipt(tmp_path, policy, seed, rank, *, tag="", sha="a" * 64, guard=0):
    positions = [rank] + [p for p in range(1, 9) if p != rank]
    record = {
        "schema": 1, "environment": "TavernGym", "completed": True,
        "agent_id": "unit-test-only", "policy": policy, "seed": seed,
        "engine_source_hash": "6d8712c93022ba11", "engine_version": "1.1.0",
        "placements": positions, "turns": 15, "decisions": 45,
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": sha if policy == "model" else None,
        "model_guard_forced_end": guard,
    }
    path = tmp_path / f"{policy}-{seed}-{tag}.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


def test_paired_heldout_rank8_no_promotion(tmp_path):
    model = [_receipt(tmp_path, "model", seed, 8) for seed in (99125, 99126, 99127)]
    baseline = [_receipt(tmp_path, "baseline", seed, rank) for seed, rank in zip((99125, 99126, 99127), (6, 8, 8))]
    result = compare(model, baseline)
    assert result["games_per_arm"] == 3
    assert result["model_mean_placement"] == 8
    assert result["baseline_mean_placement"] == pytest.approx(22 / 3)
    assert result["paired_mean_placement_delta"] == pytest.approx(2 / 3)
    assert result["model_top4_rate"] == 0
    assert result["fallback_disclosure_complete"] is True
    assert result["statistical_screen_passed_for_human_review"] is False
    assert result["champion_promoted"] is False


def test_unpaired_seeds_rejected(tmp_path):
    a = _receipt(tmp_path, "model", 42, 8)
    b = _receipt(tmp_path, "baseline", 43, 6)
    with pytest.raises(ValueError, match="Unpaired"):
        compare([a], [b])


def test_duplicate_model_seed_rejected(tmp_path):
    a = _receipt(tmp_path, "model", 42, 8, tag="a")
    b = _receipt(tmp_path, "model", 42, 8, tag="b")
    c = _receipt(tmp_path, "baseline", 42, 6)
    with pytest.raises(ValueError, match="Repeated"):
        compare([a, b], [c])


def test_fallback_does_not_count_as_raw_model(tmp_path):
    a = _receipt(tmp_path, "model", 42, 8, guard=1)
    b = _receipt(tmp_path, "baseline", 42, 6)
    with pytest.raises(ValueError, match="Guarded"):
        compare([a], [b])


def test_mixed_weight_rejected(tmp_path):
    a = _receipt(tmp_path, "model", 41, 8, sha="a" * 64)
    b = _receipt(tmp_path, "model", 42, 8, sha="b" * 64)
    c = _receipt(tmp_path, "baseline", 41, 6)
    d = _receipt(tmp_path, "baseline", 42, 8)
    with pytest.raises(ValueError, match="Mixed"):
        compare([a, b], [c, d])


def test_broken_placement_permutation_rejected(tmp_path):
    a = _receipt(tmp_path, "model", 42, 8)
    record = json.loads(a.read_text(encoding="utf-8"))
    record["placements"][1] = 8
    a.write_text(json.dumps(record), encoding="utf-8")
    b = _receipt(tmp_path, "baseline", 42, 6)
    with pytest.raises(ValueError, match="permutation"):
        compare([a], [b])


def test_incomplete_game_rejected(tmp_path):
    a = _receipt(tmp_path, "model", 42, 8)
    record = json.loads(a.read_text(encoding="utf-8"))
    record["completed"] = False
    a.write_text(json.dumps(record), encoding="utf-8")
    b = _receipt(tmp_path, "baseline", 42, 6)
    with pytest.raises(ValueError, match="Incomplete"):
        compare([a], [b])
