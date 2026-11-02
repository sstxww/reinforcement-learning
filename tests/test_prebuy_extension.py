import pytest
from tavern_ai.prebuy_extension import execute

def test_extension_game_budget_fails_before_engine_import(tmp_path):
    with pytest.raises(ValueError, match="8..24"):
        execute(36520, 36521, 0, tmp_path/"x", tmp_path/"r.json")
    with pytest.raises(ValueError, match="8..24"):
        execute(36520, 36521, 25, tmp_path/"x", tmp_path/"r.json")

def test_seed_overlap_rejected_before_engine_import(tmp_path):
    with pytest.raises(ValueError, match="differ"):
        execute(36522, 36521, 16, tmp_path/"x", tmp_path/"r.json")
