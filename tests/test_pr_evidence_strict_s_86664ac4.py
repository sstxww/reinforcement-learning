"""Synthetic unit fixtures only: NOT TavernGym match receipts or game results."""
import json

import pytest

from scripts.check_pr_evidence import main
from tavern_ai.contract import ENGINE_HASH


SESSION = "s-20261102-86664ac4"


def synthetic_shape():
    return {
        "schema": 1,
        "environment": "TavernGym",
        "completed": True,
        "agent_id": SESSION,
        "seed": 96641,
        "engine_version": "1.1.0",
        "engine_source_hash": ENGINE_HASH,
        "policy": "baseline",
        "model_sha256": None,
        "placements": list(range(1, 9)),
        "turns": 12,
        "decisions": 25,
        "truncated_combats": 0,
        "turn_limit_end": False,
    }


def invoke(tmp_path, monkeypatch, payload):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_HEAD_REF", "agent/" + SESSION + "/optimization-001")
    folder = tmp_path / "experiments" / SESSION
    folder.mkdir(parents=True)
    (folder / "synthetic-test-only.json").write_text(json.dumps(payload), encoding="utf-8")
    main()


def test_strict_valid_shape_passes(tmp_path, monkeypatch):
    invoke(tmp_path, monkeypatch, synthetic_shape())


@pytest.mark.parametrize("field,value", [
    ("placements", [1, 1, 3, 4, 5, 6, 7, 8]),
    ("engine_source_hash", "not-pinned"),
    ("engine_version", "unverified"),
    ("seed", True),
    ("truncated_combats", False),
])
def test_gate_rejects_receipt_shapes_legacy_would_accept(tmp_path, monkeypatch, field, value):
    fake = synthetic_shape()
    fake[field] = value
    with pytest.raises(ValueError):
        invoke(tmp_path, monkeypatch, fake)


def test_gate_rejects_wrong_session_identity(tmp_path, monkeypatch):
    fake = synthetic_shape()
    fake["agent_id"] = "other-session"
    with pytest.raises(SystemExit, match="identity mismatch"):
        invoke(tmp_path, monkeypatch, fake)


def test_non_pr_does_not_claim_evidence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_HEAD_REF", raising=False)
    main()
