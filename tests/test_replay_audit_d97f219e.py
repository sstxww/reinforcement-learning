"""Pure regression tests for isolated real-game replay audit logic."""
from tavern_ai.replay_audit_d97f219e import compare_replays, order_for_seeds
import pytest


def sample(seed=7, trace="abc", rank=3):
    return {
        "seed": seed, "placements": [rank, 1, 2, 4, 5, 6, 7, 8],
        "turns": 15, "decisions": 35, "truncated_combats": 0,
        "turn_limit_end": False, "trace_sha256": trace,
        "engine_version": "1.1.0", "engine_source_hash": "fingerprint",
        "timestamp": "a-unique-run-timestamp",
    }


def test_reverse_order_exposes_interleaved_rng():
    assert order_for_seeds([11, 22, 33]) == [11, 22, 33, 33, 22, 11]


@pytest.mark.parametrize("seeds", [[], [1], [1, 1], list(range(11))])
def test_seed_validation(seeds):
    with pytest.raises(ValueError, match="distinct seeds"):
        order_for_seeds(seeds)


def test_same_trace_is_reproducible_even_with_new_metadata():
    a, b = sample(), sample()
    b["timestamp"] = "different"
    b["git_sha"] = "different"
    assert compare_replays(a, b)["identical"]


def test_equal_final_rank_does_not_hide_different_actions():
    a, b = sample(), sample(trace="other")
    result = compare_replays(a, b)
    assert not result["identical"]
    assert result["different_fields"] == ["trace_sha256"]


def test_any_different_placement_fails_comparison():
    a, b = sample(), sample(rank=8)
    assert not compare_replays(a, b)["identical"]
