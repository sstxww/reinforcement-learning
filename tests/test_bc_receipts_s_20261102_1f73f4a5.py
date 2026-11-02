"""Regression: aggregate training metrics must never be treated as game receipts."""
import json
from pathlib import Path
from tavern_ai.validate_receipt import validate

ROOT = Path(__file__).resolve().parents[1] / "experiments" / "s-20261102-1f73f4a5"

def test_metrics_lives_outside_receipt_glob():
    assert not (ROOT / "summary.json").exists()
    path = ROOT / "reports" / "summary.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["session"] == "s-20261102-1f73f4a5"
    assert "teacher_agreement" in data
    assert "completed" not in data

def test_every_top_level_json_is_a_genuine_full_game_receipt():
    receipts = sorted(ROOT.glob("*.json"))
    assert len(receipts) == 4
    for path in receipts:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["agent_id"] == "s-20261102-1f73f4a5"
        assert data["completed"] is True
        validate(data)
