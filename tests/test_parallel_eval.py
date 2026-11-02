"""Unit and regression checks for isolated parallel evaluation."""
import pytest
from tavern_ai.parallel_eval import _check_parameters, compare_receipts, run_batch

def receipt(seed=1, rank=8):
    return {
        "seed": seed, "environment": "TavernGym",
        "engine_source_hash": "hash", "engine_version": "1.1.0",
        "agent_id": "test", "policy": "baseline", "completed": True,
        "turns": 14, "decisions": 50,
        "placements": [rank, 1, 2, 3, 4, 5, 6, 7],
        "truncated_combats": 0, "turn_limit_end": False, "model_sha256": None,
        "timestamp": "ignored metadata",
    }

def test_replay_agrees_without_timestamp_identity():
    a = receipt()
    b = {**a, "timestamp": "another time", "git_sha": "another build"}
    compare_receipts([a], [b])

def test_replay_detects_actions_or_placement_divergence():
    a, b = receipt(), receipt()
    b["decisions"] += 1
    with pytest.raises(ValueError, match="decisions"):
        compare_receipts([a], [b])
    b = receipt(rank=7)
    with pytest.raises(ValueError, match="placements"):
        compare_receipts([a], [b])

def test_replay_detects_seed_or_count_mismatch():
    with pytest.raises(ValueError, match="Different batch lengths"):
        compare_receipts([receipt()], [])
    with pytest.raises(ValueError, match="seed"):
        compare_receipts([receipt(1)], [receipt(2)])

@pytest.mark.parametrize("games,workers", [(0,2), (33,2), (2,0), (2,5)])
def test_bounded_workload(games,workers):
    with pytest.raises(ValueError):
        _check_parameters(games,workers)

def test_duplicate_seeds_fail_before_engine_import():
    with pytest.raises(ValueError, match="Seeds must be unique"):
        run_batch([101,101], "test", parallel=True)

def test_invalid_agent_id_fails_before_engine_import():
    with pytest.raises(ValueError, match="Invalid agent"):
        run_batch([101], "bad/id", parallel=False)
