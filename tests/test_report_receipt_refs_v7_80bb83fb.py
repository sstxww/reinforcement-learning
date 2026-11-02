"""Offline regression cases; synthetic files are NOT TavernGym game evidence."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "scripts" / "check_report_receipt_refs_v7.py"
spec = importlib.util.spec_from_file_location("check_report_receipt_refs_v7", SRC)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def setup(tmp_path: Path, refs: list[str], *, seed: int = 99385):
    (tmp_path / "reports").mkdir()
    (tmp_path / "experiments" / "session").mkdir(parents=True)
    receipt = tmp_path / "experiments" / "session" / "real.json"
    # Synthetic test fixture only; never committed as an experiment receipt.
    receipt.write_text(json.dumps({"completed": True, "seed": seed}))
    report = tmp_path / "reports" / "paired.json"
    report.write_text(json.dumps({"seed": seed, "original_receipts": refs}))
    return report, receipt


def test_valid_reference(tmp_path):
    report, receipt = setup(tmp_path, ["experiments/session/real.json"])
    assert module.checked_receipts(report, tmp_path) == [receipt]


def test_detects_dangling_report_path_from_real_pr168_regression(tmp_path):
    report, _ = setup(tmp_path, ["reports/session/001-99385-model.json"])
    with pytest.raises(module.ReceiptReferenceError, match="Unsafe or noncanonical"):
        module.checked_receipts(report, tmp_path)


@pytest.mark.parametrize("bad", ["../secret.json", "/tmp/x.json", "experiments/../reports/x.json", "experiments\\session\\real.json"])
def test_unsafe_paths_fail_closed(tmp_path, bad):
    report, _ = setup(tmp_path, [bad])
    with pytest.raises(module.ReceiptReferenceError):
        module.checked_receipts(report, tmp_path)


def test_missing_reference_fails(tmp_path):
    report, _ = setup(tmp_path, ["experiments/session/missing.json"])
    with pytest.raises(module.ReceiptReferenceError, match="Missing"):
        module.checked_receipts(report, tmp_path)


def test_incomplete_receipt_fails(tmp_path):
    report, receipt = setup(tmp_path, ["experiments/session/real.json"])
    receipt.write_text(json.dumps({"completed": False, "seed": 99385}))
    with pytest.raises(module.ReceiptReferenceError, match="not a complete"):
        module.checked_receipts(report, tmp_path)


def test_seed_mismatch_fails(tmp_path):
    report, receipt = setup(tmp_path, ["experiments/session/real.json"])
    receipt.write_text(json.dumps({"completed": True, "seed": 99386}))
    with pytest.raises(module.ReceiptReferenceError, match="seeds differ"):
        module.checked_receipts(report, tmp_path)


def test_duplicate_reference_fails(tmp_path):
    report, _ = setup(tmp_path, ["experiments/session/real.json"] * 2)
    with pytest.raises(module.ReceiptReferenceError, match="Duplicate"):
        module.checked_receipts(report, tmp_path)
