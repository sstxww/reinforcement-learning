"""Synthetic regression tests only; not a true-game or CI claim."""
import importlib.util
from pathlib import Path
import pytest
SOURCE = Path(__file__).resolve().parents[1] / "scripts/v61_pr_path_overlap_70349465.py"
spec = importlib.util.spec_from_file_location("v61_pr_overlap_70349465", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def test_train_workflow_overlap_is_a_review_flag():
    r = module.audit(
        {"number": 165, "files": [".github/workflows/train.yml", "tests/a.py"]},
        [{"number": 149, "draft": True, "files": [".github/workflows/train.yml", "tests/b.py"]}])
    assert r["overlaps"] == [{
        "pr": 149, "draft": True, "paths": [".github/workflows/train.yml"],
        "high_risk": True, "review_only": True}]
    assert r["no_overlap_is_not_merge_approval"]
    assert r["ci_receipt_release_gate"] == "not_evaluated"

def test_trainer_collision_but_distinct_session_paths():
    r = module.audit(
        {"number": 164, "files": ["tavern_ai/train.py", "research/sessions/a/STATUS.md"]},
        [{"number": 161, "files": ["tavern_ai/train.py", "research/sessions/b/STATUS.md"]},
         {"number": 167, "files": ["research/sessions/c/STATUS.md"]}])
    assert r["checked_other_prs"] == 2
    assert [item["pr"] for item in r["overlaps"]] == [161]
    assert r["overlaps"][0]["high_risk"]

@pytest.mark.parametrize("bad", [
    None, {}, {"number": 1}, {"number": True, "files": []},
    {"number": 2, "files": ["../bad"]},
    {"number": 2, "files": ["same", "same"]},
])
def test_bad_inventory_never_implies_no_conflicts(bad):
    with pytest.raises(ValueError):
        module.audit({"number": 100, "files": ["a"]}, [bad])

def test_duplicate_pr_rejected():
    with pytest.raises(ValueError):
        module.audit({"number": 165, "files": []}, [{"number": 165, "files": []}])
