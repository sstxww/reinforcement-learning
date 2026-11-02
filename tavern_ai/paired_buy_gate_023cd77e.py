"""Fail-closed single-seed raw-model BUY telemetry comparison (no strength claim).

Designed to reject invalid or assisted receipts before anyone reuses a rank-eight
observation as evidence. Works on authentic TavernGym receipts; tests are synthetic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from .receipt_integrity import validate_integrity

FAMILIES = frozenset({
    "end_turn", "buy", "sell", "upgrade", "reroll", "freeze",
    "choose", "play", "other", "hero_power", "cancel",
})


def _check(raw: dict, policy: str) -> dict:
    validate_integrity(raw)
    if raw.get("completed") is not True or raw.get("policy") != policy:
        raise ValueError("Expected complete receipt of requested unassisted policy")
    # The original trace runner explicitly records this field. Do not infer raw
    # provenance from a missing field or a successful game alone.
    if raw.get("model_guard_forced_end") != 0:
        raise ValueError("Missing or nonzero original trace guard counter")
    for key in ("fallback_actions", "guard_forced_ends", "assisted_actions"):
        value = raw.get(key, 0)
        if type(value) is not int or value != 0:
            raise ValueError("Assisted/fallback evidence is not raw model evidence")
    info = raw.get("opportunity_summary")
    if not isinstance(info, dict):
        raise ValueError("Missing recorded opportunity summary")
    counts = info.get("by_action_family")
    if not isinstance(counts, dict):
        raise ValueError("Missing action-family histogram")
    if any(type(v) is not int or v < 0 for v in counts.values()):
        raise ValueError("Invalid action-family count")
    decisions = raw.get("decisions")
    if type(decisions) is not int or decisions < 1:
        raise ValueError("Missing or invalid decisions")
    if info.get("decisions") != decisions:
        raise ValueError("Opportunity summary disagrees with game decisions")
    if sum(counts.get(k, 0) for k in FAMILIES) != decisions:
        raise ValueError("Action family counts must cover all decisions")
    legal = info.get("buy_legal_decisions")
    bought = info.get("buy_chosen")
    ended = info.get("end_while_buy_legal")
    if (type(legal) is not int or type(bought) is not int
            or type(ended) is not int or not (0 <= bought <= legal <= decisions)
            or not (0 <= ended <= legal)
            or bought != counts.get("buy", 0)):
        raise ValueError("Impossible BUY opportunity counters")
    rate = info.get("conditional_buy_rate_given_legal")
    expected = bought / legal if legal else None
    if (rate is None) != (expected is None):
        raise ValueError("BUY rate missing or impossible")
    if expected is not None and (type(rate) not in (float, int)
                                or not math.isfinite(rate)
                                or not math.isclose(rate, expected, abs_tol=1e-9)):
        raise ValueError("BUY rate inconsistent with counters")
    return {
        "rank": raw["placements"][0], "decisions": decisions,
        "buy_legal_decisions": legal, "buy_chosen": bought,
        "buy_rate_per_legal_decision": expected,
        "end_while_buy_legal": ended,
        "freeze": counts.get("freeze", 0),
        "reroll": counts.get("reroll", 0),
        "other": counts.get("other", 0),
    }


def compare(baseline: dict, candidate: dict, expected_sha256: str) -> dict:
    if (not isinstance(expected_sha256, str) or len(expected_sha256) != 64
            or any(c not in "0123456789abcdef" for c in expected_sha256)):
        raise ValueError("Expected exact lowercase source checkpoint SHA256")
    b = _check(baseline, "baseline")
    m = _check(candidate, "model")
    if baseline["seed"] != candidate["seed"]:
        raise ValueError("Not a same-seed paired comparison")
    if baseline.get("engine_source_hash") != candidate.get("engine_source_hash"):
        raise ValueError("Engine source does not match")
    if baseline.get("seat", 0) != 0 or candidate.get("seat", 0) != 0:
        raise ValueError("Comparison requires controlled seat zero")
    if candidate.get("model_sha256") != expected_sha256:
        raise ValueError("Model digest differs from registered source")
    if baseline.get("model_sha256") is not None:
        raise ValueError("Baseline must not use model weights")
    return {
        "schema": 1, "sample_size": 1, "seed": baseline["seed"],
        "controlled_seat": 0, "engine_source_hash": baseline["engine_source_hash"],
        "source_model_sha256": expected_sha256,
        "baseline": b, "raw_model": m,
        "mean_placement_delta_model_minus_baseline": m["rank"] - b["rank"],
        "result": "descriptive_single_seed_only_no_performance_claim",
        "caveat": "BUY-legal decision exposures are temporally dependent and do not establish affordable independent purchase opportunities.",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--model-sha", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    b = json.loads(a.baseline.read_text())
    c = json.loads(a.candidate.read_text())
    report = compare(b, c, a.model_sha)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
