import pytest
from tavern_ai.paired_receipt_gate_30fe4978 import compare
from tavern_ai.contract import ENGINE_HASH


def receipt(seed, policy, rank):
    placements = [rank] + [i for i in range(1, 9) if i != rank]
    return {"environment": "TavernGym", "engine_version": "1.1.0",
            "engine_source_hash": ENGINE_HASH, "completed": True,
            "agent_id": "s-20261102-30fe4978", "policy": policy,
            "model_sha256": "a" * 64 if policy == "model" else None,
            "seed": seed, "placements": placements, "turns": 10,
            "decisions": 100, "truncated_combats": 0, "turn_limit_end": False}


def test_exact_paired_seed_comparison():
    r = compare([receipt(42, "model", 8), receipt(41, "model", 7)],
                [receipt(41, "baseline", 6), receipt(42, "baseline", 7)])
    assert r["seeds"] == [41, 42]
    assert r["candidate_minus_baseline_rank_deltas"] == [1, 1]
    assert r["mean_rank_delta"] == 1
    assert r["champion_promotion_eligible"] is False


@pytest.mark.parametrize("mutate", [
    lambda r: r.update(completed=False),
    lambda r: r.update(policy="guarded_model"),
    lambda r: r.update(guard_forced_ends=1),
    lambda r: r.update(raw_model_only=False),
    lambda r: r.update(model_sha256=None),
    lambda r: r.update(engine_source_hash="bad"),
    lambda r: r.update(seat=5),
    lambda r: r.update(placements=[8] * 8),
])
def test_rejects_incomplete_assisted_or_incompatible_model(mutate):
    r = receipt(41, "model", 8)
    mutate(r)
    with pytest.raises(ValueError):
        compare([r], [receipt(41, "baseline", 6)])


def test_rejects_mismatched_seeds():
    with pytest.raises(ValueError, match="paired"):
        compare([receipt(41, "model", 8)], [receipt(42, "baseline", 6)])


def test_rejects_mixed_model_hashes():
    r = receipt(42, "model", 8)
    r["model_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="Different"):
        compare([receipt(41, "model", 8), r],
                [receipt(41, "baseline", 6), receipt(42, "baseline", 7)])


def test_rejects_duplicate_seed():
    with pytest.raises(ValueError, match="duplicate"):
        compare([receipt(41, "model", 8)] * 2, [receipt(41, "baseline", 6)])
