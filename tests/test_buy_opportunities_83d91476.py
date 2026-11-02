"""Synthetic telemetry unit tests; real-game claims require separate Actions evidence."""
import pytest
from tavern_ai.buy_opportunities_83d91476 import Opportunities, summary


def mask(*ids):
    out = [False] * 245
    for i in ids:
        out[i] = True
    return out


def receipt(rank, diag, forced=False):
    return {
        "environment": "TavernGym", "completed": True, "agent_id": "unit-test",
        "placements": [rank] + [x for x in range(1, 9) if x != rank],
        "turns": 12, "decisions": 3, "truncated_combats": 0,
        "turn_limit_end": False, "guarded": forced,
        "opportunity_diagnostics": {"counts": diag},
    }


def test_no_buy_action_is_not_evidence_without_legal_opportunity():
    o = Opportunities()
    o.observe(1, mask(0), 0)
    assert o.report()["counts"].get("buys", 0) == 0
    assert o.report()["counts"].get("buy_legal_exposures", 0) == 0
    assert o.report()["buy_given_legal_exposure_rate"] is None


def test_policy_ends_while_buy_was_legal():
    o = Opportunities()
    o.observe(1, mask(0, 8, 9), 0)
    o.observe(2, mask(0, 8), 8)
    r = o.report()
    assert r["counts"]["buy_legal_exposures"] == 2
    assert r["counts"]["policy_end_with_buy_legal"] == 1
    assert r["buy_given_legal_exposure_rate"] == 0.5
    assert r["buy_legal_turns"] == 2
    assert r["turns_with_buy"] == 1


def test_forced_end_not_counted_as_policy_failure():
    o = Opportunities()
    o.observe(3, mask(0, 8), 0, forced=True)
    r = o.report()["counts"]
    assert r["guard_forced_end"] == 1
    assert r.get("policy_end_with_buy_legal", 0) == 0


def test_reject_illegal_and_bad_guard():
    o = Opportunities()
    with pytest.raises(ValueError, match="Illegal action"):
        o.observe(1, mask(0), 8)
    with pytest.raises(ValueError, match="Guard"):
        o.observe(1, mask(0, 8), 8, forced=True)
    with pytest.raises(ValueError, match="245"):
        o.observe(1, [True], 0)


def test_summarize_guarded_separately():
    r = summary([
        receipt(8, {"buy_legal_exposures": 5, "buys": 0,
                    "policy_end_with_buy_legal": 4}),
        receipt(7, {"buy_legal_exposures": 5, "buys": 2, "guard_forced_end": 1}, True),
    ])
    assert r["mean_rank"] == 7.5
    assert r["total_buy_legal_exposures"] == 10
    assert r["total_buys"] == 2
    assert r["candidate_pure_model_games"] == 1
