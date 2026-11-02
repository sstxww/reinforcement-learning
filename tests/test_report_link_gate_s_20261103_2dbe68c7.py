"""Synthetic-only regression tests: NOT authentic TavernGym match receipts."""
import json
from pathlib import Path

import pytest

from tavern_ai.report_link_gate_v7 import verify_report

SESSION = "s-20261103-2dbe68c7"
DIGEST = "a" * 64
SEED = 99737


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _receipt(policy: str) -> dict:
    return {
        "schema": 1, "environment": "TavernGym", "completed": True,
        "agent_id": SESSION, "policy": policy, "seed": SEED,
        "engine_version": "1.1.0",
        "engine_source_hash": "6d8712c93022ba11",
        "placements": [7, 2, 6, 4, 5, 8, 1, 3] if policy == "baseline"
                      else [8, 1, 6, 5, 4, 2, 3, 7],
        "turns": 16, "decisions": 40,
        "truncated_combats": 0, "turn_limit_end": False,
        "model_sha256": None if policy == "baseline" else DIGEST,
    }


def _setup(tmp_path):
    refs = [f"experiments/{SESSION}/001-{SEED}-{p}.json"
            for p in ("baseline", "model")]
    for ref, policy in zip(refs, ("baseline", "model")):
        _write(tmp_path / ref, _receipt(policy))
    report = {
        "session_id": SESSION, "kind": "single_seed_descriptive_paired_real_game",
        "seed": SEED, "controlled_seat": 0, "original_receipts": refs,
        "registered_model_sha256": DIGEST,
        "baseline_placement": 7, "model_placement": 8,
        "model_minus_baseline_placement": 1,
        "games_completed": 2, "sample_n_per_policy": 1,
    }
    report_path = tmp_path / "reports" / SESSION / "paired.json"
    _write(report_path, report)
    return report_path, report


def test_valid_committed_paired_links(tmp_path):
    path, _ = _setup(tmp_path)
    result = verify_report(path, tmp_path)
    assert result["linked_receipts"] == 2
    assert (result["baseline_rank"], result["model_rank"]) == (7, 8)


def test_rejects_ephemeral_runner_paths(tmp_path):
    path, report = _setup(tmp_path)
    report["original_receipts"] = [
        f"reports/{SESSION}/001-{SEED}-baseline.json",
        f"reports/{SESSION}/001-{SEED}-model.json",
    ]
    _write(path, report)
    with pytest.raises(ValueError, match="committed session experiments"):
        verify_report(path, tmp_path)


def test_rejects_escape_or_absolute_paths(tmp_path):
    path, report = _setup(tmp_path)
    for value in ("../private.json", "/tmp/private.json", "experiments/other/001.json"):
        report["original_receipts"][0] = value
        _write(path, report)
        with pytest.raises(ValueError):
            verify_report(path, tmp_path)


def test_rejects_report_digest_mismatch(tmp_path):
    path, report = _setup(tmp_path)
    report["registered_model_sha256"] = "b" * 64
    _write(path, report)
    with pytest.raises(ValueError, match="SHA256 differs"):
        verify_report(path, tmp_path)


def test_rejects_misreported_placement(tmp_path):
    path, report = _setup(tmp_path)
    report["model_placement"] = 1
    _write(path, report)
    with pytest.raises(ValueError, match="rank summary"):
        verify_report(path, tmp_path)


def test_rejects_duplicate_policy_or_wrong_seed(tmp_path):
    path, report = _setup(tmp_path)
    model_ref = report["original_receipts"][1]
    _write(tmp_path / model_ref, _receipt("baseline"))
    with pytest.raises(ValueError, match="Expected one"):
        verify_report(path, tmp_path)
    bad = _receipt("model")
    bad["seed"] = SEED + 1
    _write(tmp_path / model_ref, bad)
    with pytest.raises(ValueError, match="seed differs"):
        verify_report(path, tmp_path)
