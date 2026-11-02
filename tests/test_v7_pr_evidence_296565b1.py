"""Regression tests for PR-only raw/unassisted evidence gate.

All receipts in this module are synthetic fixtures, NOT TavernGym games.
"""
import json

import pytest

from scripts.check_pr_evidence import main, require_unassisted
from tavern_ai.receipt_integrity import validate_integrity


ASSISTANCE_COUNTERS = (
    "guard_forced_end",
    "guard_forced_ends",
    "forced_end_count",
    "fallback_count",
    "fallback_actions",
    "safety_fallback_count",
)


def example_receipt(policy="baseline"):
    row = {
        "schema": 1,
        "environment": "TavernGym",
        "completed": True,
        "agent_id": "s-20261103-296565b1",
        "placements": [4, 1, 2, 3, 5, 6, 7, 8],
        "turns": 12,
        "decisions": 42,
        "truncated_combats": 0,
        "turn_limit_end": False,
        "seed": 94773,
        "engine_version": "1.1.0",
        "engine_source_hash": "6d8712c93022ba11",
        "policy": policy,
        "model_sha256": "a" * 64 if policy == "model" else None,
    }
    validate_integrity(row)
    return row


@pytest.mark.parametrize("policy", ["baseline", "model"])
def test_clean_receipts_accepted(policy):
    row = example_receipt(policy)
    require_unassisted(row)
    row["opportunity_diagnostics"] = {
        "counts": {"fallback_actions": 0, "guard_forced_ends": 0, "buy": 3}
    }
    require_unassisted(row)


@pytest.mark.parametrize("name", ASSISTANCE_COUNTERS)
@pytest.mark.parametrize("location", ["top", "nested"])
@pytest.mark.parametrize("value", [1, -1, True, None, 1.5])
def test_all_assistance_aliases_fail_closed(name, location, value):
    row = example_receipt("model")
    if location == "top":
        row[name] = value
    else:
        row["opportunity_diagnostics"] = {"counts": {name: value}}
    with pytest.raises(ValueError, match="Assisted or malformed"):
        require_unassisted(row)


@pytest.mark.parametrize("marker,bad_value", [
    ("guarded", True),
    ("assisted", True),
    ("policy_fallback_used", True),
    ("raw_model_only", False),
    ("guarded", 0),
])
def test_explicit_assistance_markers_not_accepted(marker, bad_value):
    row = example_receipt("model")
    row[marker] = bad_value
    with pytest.raises(ValueError, match="not unassisted|disclaims"):
        require_unassisted(row)


@pytest.mark.parametrize("bad", [None, [], "invalid", {"counts": None}])
def test_malformed_opportunity_diagnostics_rejected(bad):
    row = example_receipt()
    row["opportunity_diagnostics"] = bad
    with pytest.raises(ValueError, match="Malformed"):
        require_unassisted(row)


def test_real_pr_entrypoint_rejects_hidden_fallback(tmp_path, monkeypatch):
    # A synthetic receipt passes original identity/full-game structure checks.
    # This tests the additional guard without pretending it is a live match.
    agent = "s-20261103-296565b1"
    folder = tmp_path / "experiments" / agent
    folder.mkdir(parents=True)
    path = folder / "001-synthetic.json"
    row = example_receipt("model")
    row["fallback_actions"] = 1
    path.write_text(json.dumps(row), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_HEAD_REF", f"agent/{agent}/optimization-001")
    with pytest.raises(ValueError, match="fallback_actions"):
        main()
    row["fallback_actions"] = 0
    path.write_text(json.dumps(row), encoding="utf-8")
    main()
