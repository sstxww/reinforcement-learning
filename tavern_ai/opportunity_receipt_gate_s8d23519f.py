"""Fail-closed consistency audit for optional public BUY-opportunity game telemetry.

A valid eight-seat receipt is necessary, not proof that action telemetry is true.
This gate detects internal contradictions, never reconstructs hidden opponents,
never treats synthetic test fixtures as game evidence, and never changes a policy.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .buy_opportunity_68099929 import classify
from .receipt_integrity import validate_integrity

FAMILIES = ("end_turn", "reroll", "freeze", "upgrade", "buy", "sell", "choose", "play", "other")
COUNTERS = ("buy_legal_decisions", "end_while_buy_legal", "all_end_turns", "consecutive_identical_public_observation")


def _count(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def _rate(actual: object, numerator: int, denominator: int, name: str) -> None:
    if denominator == 0:
        if actual is not None:
            raise ValueError(f"{name}: undefined zero-denominator rate must be null")
    elif (type(actual) not in (float, int) or
          not math.isfinite(actual) or
          not math.isclose(float(actual), numerator / denominator, rel_tol=1e-10, abs_tol=1e-10)):
        raise ValueError(f"{name}: inconsistent numerator/denominator")


def audit(receipt: dict) -> dict:
    """Validate a completed game's declared public-action aggregate and prefix.

    Return only evidence labels and simple counts, no claims about model quality.
    """
    validate_integrity(receipt)
    summary = receipt.get("opportunity_summary")
    if not isinstance(summary, dict):
        raise ValueError("Missing opportunity_summary; not a telemetry receipt")
    decisions = _count(receipt["decisions"], "decisions")
    if _count(summary.get("decisions"), "summary.decisions") != decisions:
        raise ValueError("Decision count mismatch")
    family_counts = summary.get("by_action_family")
    if not isinstance(family_counts, dict):
        raise ValueError("Missing by_action_family")
    if set(family_counts) - set(FAMILIES) - set(COUNTERS):
        raise ValueError("Unrecognized action family/counter")
    families = {k: _count(family_counts.get(k, 0), f"family.{k}") for k in FAMILIES}
    if sum(families.values()) != decisions:
        raise ValueError("Action-family counts do not total decisions")
    buy = families["buy"]
    legal = _count(summary.get("buy_legal_decisions"), "buy_legal_decisions")
    end_legal = _count(summary.get("end_while_buy_legal"), "end_while_buy_legal")
    if legal < buy or legal > decisions or end_legal > min(legal, families["end_turn"]):
        raise ValueError("Impossible BUY opportunity counts")
    if _count(summary.get("buy_chosen"), "buy_chosen") != buy:
        raise ValueError("BUY chosen disagrees with action families")
    if _count(summary.get("all_end_turns"), "all_end_turns") != families["end_turn"]:
        raise ValueError("END count disagrees with action families")
    for k, expected in (("buy_legal_decisions", legal),
                        ("end_while_buy_legal", end_legal),
                        ("all_end_turns", families["end_turn"])):
        if k in family_counts and _count(family_counts[k], f"family.{k}") != expected:
            raise ValueError(f"Duplicate counter disagrees: {k}")
    turns_with_buy = _count(summary.get("distinct_turns_with_legal_buy"), "distinct_turns_with_legal_buy")
    states_with_buy = _count(summary.get("unique_public_states_with_legal_buy"), "unique_public_states_with_legal_buy")
    turns_end_legal = _count(summary.get("turns_with_end_while_buy_legal"), "turns_with_end_while_buy_legal")
    duplicate_states = _count(summary.get("consecutive_identical_public_observation"),
                              "consecutive_identical_public_observation")
    if (turns_with_buy > legal or states_with_buy > legal or
        turns_end_legal > min(turns_with_buy, end_legal) or duplicate_states > decisions):
        raise ValueError("Impossible turn/state counters")
    if (legal > 0 and (turns_with_buy == 0 or states_with_buy == 0)) or (legal == 0 and
             (turns_with_buy or states_with_buy)):
        raise ValueError("BUY opportunity turn/state count mismatch")
    if "consecutive_identical_public_observation" in family_counts and (
        _count(family_counts["consecutive_identical_public_observation"], "family.duplicate_states")
        != duplicate_states
    ):
        raise ValueError("Duplicate-state counter disagrees")
    _rate(summary.get("conditional_buy_rate_given_legal"), buy, legal,
          "conditional_buy_rate_given_legal")
    _rate(summary.get("conditional_end_rate_given_legal_buy"), end_legal, legal,
          "conditional_end_rate_given_legal_buy")
    guard = _count(receipt.get("model_guard_forced_end", 0), "model_guard_forced_end")
    if guard:
        raise ValueError("Assisted/guarded receipt cannot pass raw telemetry gate")
    if receipt.get("policy_variant") not in (None, "raw", "raw_maskable_ppo", "baseline"):
        raise ValueError("Assisted/non-raw policy variant is not raw evidence")
    trace = receipt.get("trace_first_32")
    if not isinstance(trace, list) or len(trace) > min(32, decisions):
        raise ValueError("Invalid public trace prefix")
    observed = {name: 0 for name in FAMILIES}
    prefix_legal = 0
    for i, e in enumerate(trace):
        if not isinstance(e, dict):
            raise ValueError(f"Trace {i}: invalid item")
        action = e.get("action")
        if type(action) is not int or not 0 <= action < 245:
            raise ValueError(f"Trace {i}: invalid action")
        family = classify(action)
        if e.get("family") != family:
            raise ValueError(f"Trace {i}: action taxonomy mismatch")
        turn = _count(e.get("turn"), f"trace.{i}.turn")
        legal_buy_count = _count(e.get("legal_buy_count"), f"trace.{i}.legal_buy_count")
        if legal_buy_count > 8 or type(e.get("buy_legal")) is not bool:
            raise ValueError(f"Trace {i}: invalid BUY mask exposure")
        legal_now = legal_buy_count > 0
        if e["buy_legal"] != legal_now or (family == "buy" and not legal_now):
            raise ValueError(f"Trace {i}: BUY mask/action conflict")
        if type(e.get("same_public_state_as_prior")) is not bool:
            raise ValueError(f"Trace {i}: missing public-state flag")
        if i and turn < trace[i - 1]["turn"]:
            raise ValueError(f"Trace {i}: nonmonotone game turn")
        observed[family] += 1
        prefix_legal += int(legal_now)
    if any(observed[k] > families[k] for k in FAMILIES) or prefix_legal > legal:
        raise ValueError("Trace prefix exceeds full-game aggregate")
    return {
        "policy": receipt["policy"],
        "model_sha256": receipt.get("model_sha256"),
        "seed": receipt["seed"],
        "seat_zero_placement": receipt["placements"][0],
        "decisions": decisions,
        "public_trace_prefix_length": len(trace),
        "legal_buy_decisions": legal,
        "buy_chosen": buy,
        "raw_unassisted": True,
        "note": "Internal-consistency audit only; source authenticity and competitive strength require independent evidence.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    result = audit(json.loads(args.receipt.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
