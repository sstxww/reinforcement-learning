"""Synthetic *validation-only* fixtures. No fixture represents a played match."""
import json

import pytest

from scripts.check_pr_evidence import main
from tavern_ai.contract import ENGINE_HASH


SESSION = "s-20261102-dfa88e31"


def synthetic_receipt():
    return {
        "schema": 1, "environment": "TavernGym", "agent_id": SESSION,
        "completed": True, "seed": 801231, "turns": 15,
        "decisions": 55, "placements": list(range(1, 9)),
        "policy": "baseline", "model_sha256": None,
        "engine_version": "1.1.0", "engine_source_hash": ENGINE_HASH,
        "truncated_combats": 0, "turn_limit_end": False,
    }


def check(tmp_path, monkeypatch, receipt):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_HEAD_REF", f"agent/{SESSION}/optimization-001")
    path = tmp_path / "experiments" / SESSION / "synthetic-validation-only.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(receipt), encoding="utf-8")
    main()


def test_valid_synthetic_structure_passes(tmp_path, monkeypatch):
    check(tmp_path, monkeypatch, synthetic_receipt())


@pytest.mark.parametrize("mutation", [
    "duplicate_placement", "engine_version", "engine_source_hash",
    "seed_missing", "policy", "wrong_model_hash", "truncation",
])
def test_incorrect_evidence_rejected(tmp_path, monkeypatch, mutation):
    case = synthetic_receipt()
    if mutation == "duplicate_placement":
        case["placements"][-1] = 1
    elif mutation == "engine_version":
        case["engine_version"] = "0.0.0"
    elif mutation == "engine_source_hash":
        case["engine_source_hash"] = "unverified"
    elif mutation == "seed_missing":
        case.pop("seed")
    elif mutation == "policy":
        case["policy"] = "model"
    elif mutation == "wrong_model_hash":
        case["model_sha256"] = "0" * 64
    elif mutation == "truncation":
        case["truncated_combats"] = 1
    with pytest.raises(ValueError):
        check(tmp_path, monkeypatch, case)


def test_forged_path_without_receipt_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_HEAD_REF", f"agent/{SESSION}/optimization-001")
    with pytest.raises(SystemExit, match="Missing independent"):
        main()


def test_guarded_model_diagnostic_receipt_is_valid_but_not_plain_ppo(tmp_path, monkeypatch):
    case = synthetic_receipt()
    case["policy"] = "model_guarded"
    case["model_sha256"] = "a" * 64
    case["guarded"] = True
    check(tmp_path, monkeypatch, case)


def test_guarded_diagnostic_must_have_model_hash(tmp_path, monkeypatch):
    case = synthetic_receipt()
    case["policy"] = "model_with_explicit_buy_override"
    with pytest.raises(ValueError, match="checkpoint SHA256"):
        check(tmp_path, monkeypatch, case)


def test_guarded_diagnostic_cannot_bypass_permutation_and_engine(tmp_path, monkeypatch):
    case = synthetic_receipt()
    case["policy"] = "model_guarded"
    case["model_sha256"] = "b" * 64
    case["placements"][7] = 1
    with pytest.raises(ValueError, match="permutation"):
        check(tmp_path, monkeypatch, case)
    case["placements"] = list(range(1, 9))
    case["engine_source_hash"] = "untrusted"
    with pytest.raises(ValueError, match="engine"):
        check(tmp_path, monkeypatch, case)
