"""Non-network regression suite for isolated V5 paired evidence contract."""
import pytest
from tavern_ai.paired_evidence_s_5ce8a1d4 import compare


def rec(seed=101, ranks=None, policy="baseline"):
    return {
        "schema": 1, "environment": "TavernGym", "engine_version": "1.1.0",
        "engine_source_hash": "6d8712c93022ba11",
        "completed": True, "turn_limit_end": False, "truncated_combats": 0,
        "seed": seed, "placements": ranks or list(range(1, 9)),
        "decisions": 50, "policy": policy,
        "model_sha256": "a" * 64 if policy == "model" else None,
    }


def test_negative_control_same_raw_baseline():
    result = compare([rec()], [rec()], seats=[0])
    assert result["mean_delta_candidate_minus_baseline"] == 0
    assert result["bootstrap_95pct_interval_if_n_at_least_10"] is None
    assert result["champion_promoted"] is False


def test_seat_rotation_does_not_assume_zero():
    base = rec(ranks=[8, 7, 6, 5, 4, 3, 2, 1])
    cand = rec(ranks=[8, 7, 6, 4, 5, 3, 2, 1])
    assert compare([base], [cand], seats=[3])["mean_delta_candidate_minus_baseline"] == -1


def test_reject_unpaired_seed():
    with pytest.raises(ValueError, match="Seed mismatch"):
        compare([rec(101)], [rec(102)], seats=[0])


def test_reject_duplicate_seed_seat():
    with pytest.raises(ValueError, match="Duplicate"):
        compare([rec(), rec()], [rec(), rec()], seats=[0, 0])


@pytest.mark.parametrize("field,bad", [
    ("completed", False), ("turn_limit_end", True), ("truncated_combats", 1),
])
def test_reject_incomplete_or_truncated_games(field, bad):
    r = rec()
    r[field] = bad
    with pytest.raises(ValueError):
        compare([r], [rec()], seats=[0])


def test_reject_fabricated_rank_permutation():
    r = rec()
    r["placements"] = [8] * 8
    with pytest.raises(ValueError, match="permutation"):
        compare([r], [rec()], seats=[0])


def test_reject_unlabeled_guarded_candidate():
    with pytest.raises(ValueError, match="requires"):
        compare([rec()], [rec(policy="model")], seats=[0], candidate_mode="guarded")


def test_reject_raw_fallback_mislabel():
    with pytest.raises(ValueError, match="Raw-policy"):
        compare([rec()], [rec()], seats=[0], candidate_fallbacks=[1])


def test_guarded_model_has_explicit_separate_fallback_telemetry():
    report = compare([rec()], [rec(policy="model")], seats=[0],
                     candidate_mode="guarded", candidate_fallbacks=[2])
    assert report["candidate_mode"] == "guarded"
    assert report["pairs"][0]["candidate_fallback_count"] == 2


def test_model_checkpoint_sha_required():
    r = rec(policy="model")
    r["model_sha256"] = "garbage"
    with pytest.raises(ValueError, match="SHA256"):
        compare([rec()], [r], seats=[0])


def test_reject_missing_or_unaligned_explicit_seats():
    with pytest.raises(ValueError):
        compare([rec()], [], seats=[0])
    with pytest.raises(ValueError):
        compare([rec()], [rec()], seats=[])


def test_bootstrap_is_reproducible_on_ten_distinct_pairs():
    b = [rec(s) for s in range(10)]
    report = compare(b, b, seats=[0] * 10)
    assert report["bootstrap_95pct_interval_if_n_at_least_10"] == [0, 0]
