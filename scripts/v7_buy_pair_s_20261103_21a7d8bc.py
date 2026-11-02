"""Fail-closed matched-seed raw PPO BUY audit for one independent V7 run.

Does not infer the cause of a rank or certify a better model. The two receipts
must originate from genuine completed games; synthetic fixtures are tests only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tavern_ai.receipt_integrity import validate_integrity


def audit_pair(baseline: dict, raw_model: dict, agent_id: str,
               expected_model_sha256: str) -> dict:
    if not agent_id.startswith("s-20261103-") or len(expected_model_sha256) != 64:
        raise ValueError("Expected explicit independent session and model digest")
    for r, expected_policy in ((baseline, "baseline"), (raw_model, "model")):
        validate_integrity(r)
        if r["agent_id"] != agent_id or r["policy"] != expected_policy:
            raise ValueError("Receipt agent/policy identity mismatch")
        if r.get("seat", 0) != 0:
            raise ValueError("Only matched seat zero is certified")
        if any(type(r.get(k, 0)) is not int or r.get(k, 0) != 0
               for k in ("fallback_actions", "guard_forced_ends",
                         "model_guard_forced_end")):
            raise ValueError("Assisted, guarded or unaccounted policy actions")
        s = r.get("opportunity_summary")
        if not isinstance(s, dict):
            raise ValueError("Missing real masked-BUY opportunity telemetry")
        decisions = s.get("decisions")
        legal = s.get("buy_legal_decisions")
        buys = s.get("buy_chosen")
        if any(type(x) is not int for x in (decisions, legal, buys)):
            raise ValueError("BUY telemetry counts must be integers")
        if decisions != r["decisions"] or not 0 <= buys <= legal <= decisions:
            raise ValueError("Inconsistent BUY opportunity/decision counts")
        if s.get("conditional_buy_rate_given_legal") != (
            buys / legal if legal else None
        ):
            raise ValueError("Reported conditional BUY rate differs from counts")
    if baseline["seed"] != raw_model["seed"]:
        raise ValueError("Unpaired seeds must not be compared as matched")
    if raw_model["model_sha256"] != expected_model_sha256:
        raise ValueError("Unrecognized raw PPO checkpoint digest")
    if baseline.get("model_sha256") is not None:
        raise ValueError("Baseline must not load model weights")
    return {
        "schema": 1,
        "scope": "one matched TavernGym seed; seat zero versus seven scripted bots",
        "seed": baseline["seed"], "seat": 0, "agent_id": agent_id,
        "engine_source_hash": raw_model["engine_source_hash"],
        "model_sha256": raw_model["model_sha256"],
        "baseline": {
            "placement": baseline["placements"][0],
            "decisions": baseline["decisions"],
            "legal_buy_exposures": baseline["opportunity_summary"]["buy_legal_decisions"],
            "buys": baseline["opportunity_summary"]["buy_chosen"],
        },
        "raw_model": {
            "placement": raw_model["placements"][0],
            "decisions": raw_model["decisions"],
            "legal_buy_exposures": raw_model["opportunity_summary"]["buy_legal_decisions"],
            "buys": raw_model["opportunity_summary"]["buy_chosen"],
        },
        "paired_placement_delta_model_minus_baseline":
            raw_model["placements"][0] - baseline["placements"][0],
        "model_strength_improved": False,
        "evidence_limit": "n=1; masked BUY is a legal opportunity, not guaranteed value; no causal inference",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--raw-model", type=Path, required=True)
    p.add_argument("--agent-id", required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    report = audit_pair(json.loads(a.baseline.read_text()),
                        json.loads(a.raw_model.read_text()),
                        a.agent_id, a.expected_sha256)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
