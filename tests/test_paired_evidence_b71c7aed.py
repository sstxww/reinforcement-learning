"""Pure unit tests for raw-policy paired report invariants."""
import pytest
from tavern_ai.paired_evidence_b71c7aed import summarize_pairs

SHA = "a" * 64


def receipt(seed, policy, rank, legal=5, buys=1, missed=2):
    return {
        "completed": True, "policy": policy, "seed": seed,
        "placements": [rank] + [n for n in range(1, 9) if n != rank],
        "model_sha256": SHA if policy == "model" else None,
        "model_guard_forced_end": 0,
        "opportunity_summary": {
            "buy_legal_decisions": legal, "buy_chosen": buys,
            "end_while_buy_legal": missed, "decisions": 20,
        },
    }


def pair(seed, candidate_rank=8, baseline_rank=7):
    return {"seed": seed, "model": receipt(seed, "model", candidate_rank),
            "baseline": receipt(seed, "baseline", baseline_rank)}


def test_strict_paired_evidence():
    report = summarize_pairs([pair(101), pair(102, 8, 6)], "unpromoted", SHA)
    assert report["n_paired_games"] == 2
    assert report["candidate"]["mean_rank"] == 8
    assert report["paired_rank_delta_candidate_minus_baseline"] == 1.5
    assert report["candidate"]["buy_given_legal"] == pytest.approx(0.2)
    assert report["promoted"] is False
    assert report["seat_rotation"] is False


def test_no_legal_buy_is_unknown_not_zero_buy_competence():
    p = pair(103)
    for policy in ("model", "baseline"):
        p[policy]["opportunity_summary"].update(
            buy_legal_decisions=0, buy_chosen=0, end_while_buy_legal=0)
    assert summarize_pairs([p], "unpromoted", SHA)["candidate"]["buy_given_legal"] is None


@pytest.mark.parametrize("mutate", [
    lambda p: p["model"].update(completed=False),
    lambda p: p["model"].update(model_sha256="wrong"),
    lambda p: p["model"].update(model_guard_forced_end=3),
    lambda p: p["model"].update(seed=999),
    lambda p: p["model"]["opportunity_summary"].update(buy_chosen=999),
    lambda p: p["baseline"].update(model_sha256=SHA),
])
def test_rejects_invalid_and_fallback_games(mutate):
    p = pair(101)
    mutate(p)
    with pytest.raises(ValueError):
        summarize_pairs([p], "unpromoted", SHA)


def test_duplicate_seed_rejected():
    with pytest.raises(ValueError, match="Repeated random seed"):
        summarize_pairs([pair(101), pair(101)], "unpromoted", SHA)


def test_empty_rejected():
    with pytest.raises(ValueError):
        summarize_pairs([], "unpromoted", SHA)
