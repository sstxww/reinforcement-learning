"""Strict read-only paired evaluation of existing TavernGym v1 match receipts.

Evaluates evidence custody, not gameplay strategy or model strength. No GitHub
mutation or inference. No claim of fallback-free policy from schema-1 receipts.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

ENGINE = ("TavernGym", "1.1.0", "6d8712c93022ba11")
HEX = set("0123456789abcdef")


def is_hex(value: object, size: int) -> bool:
    return isinstance(value, str) and len(value) == size and set(value) <= HEX


def validate(record: dict, policy: str) -> None:
    """Do not silently turn broken/guarded receipts into scored games."""
    if not isinstance(record, dict) or record.get("schema") != 1:
        raise ValueError("Expected schema-1 JSON match receipt")
    if (record.get("environment"), record.get("engine_version"),
            record.get("engine_source_hash")) != ENGINE:
        raise ValueError("Engine contract/fingerprint mismatch")
    if record.get("completed") is not True:
        raise ValueError("Incomplete match")
    places = record.get("placements")
    if not isinstance(places, list) or [x for x in places if type(x) is int] != places or sorted(places) != list(range(1, 9)):
        raise ValueError("Placements must be a complete permutation of 1..8")
    if record.get("policy") != policy:
        raise ValueError("Policy arm mislabeled")
    if record.get("truncated_combats") != 0 or record.get("turn_limit_end") is not False:
        raise ValueError("Engine truncation or safety limit")
    if (type(record.get("seed")) is not int or record["seed"] < 0 or
        type(record.get("turns")) is not int or record["turns"] <= 0 or
        type(record.get("decisions")) is not int or record["decisions"] <= 0):
        raise ValueError("Invalid seed/turn/decision counters")
    if not isinstance(record.get("agent_id"), str) or not record["agent_id"].strip():
        raise ValueError("Missing agent ID")
    if not is_hex(record.get("git_sha"), 40):
        raise ValueError("Unverifiable source commit SHA")
    if policy == "model" and not is_hex(record.get("model_sha256"), 64):
        raise ValueError("Model arm lacks weight SHA256")
    if policy == "baseline" and record.get("model_sha256") is not None:
        raise ValueError("Baseline receipt contains model SHA")
    # If any optional guard/fallback counters are present, they must be zero.
    # Their absence is UNKNOWN, not proof of zero interventions.
    for k in ("forced_end_turns", "baseline_fallback_actions", "fallback_actions", "illegal_actions"):
        if k in record and (type(record[k]) is not int or record[k] != 0):
            raise ValueError("Nonzero/invalid guard, fallback, or illegal action: " + k)


def index_arm(records: list[dict], policy: str) -> dict[int, dict]:
    out = {}
    if not records:
        raise ValueError("At least one game per arm is required")
    for rec in records:
        validate(rec, policy)
        if rec["seed"] in out:
            raise ValueError("Duplicate seed in " + policy)
        out[rec["seed"]] = rec
    return out


def wilson_95(count: int, total: int) -> list[float]:
    z = 1.959963984540054
    p = count / total
    den = 1 + z * z / total
    mid = (p + z * z / (2 * total)) / den
    half = z * math.sqrt(p * (1-p) / total + z*z / (4 * total * total)) / den
    return [round(max(0.0, mid-half), 6), round(min(1.0, mid+half), 6)]


def arm_stats(rows: list[dict]) -> dict:
    ranks = [r["placements"][0] for r in rows]
    return {
        "games_completed": len(rows),
        "ranks": ranks,
        "mean_rank": statistics.mean(ranks),
        "first_place_rate": sum(x == 1 for x in ranks) / len(ranks),
        "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
        "top4_wilson_95": wilson_95(sum(x <= 4 for x in ranks), len(ranks)),
        "mean_turns": statistics.mean(r["turns"] for r in rows),
        "mean_decisions": statistics.mean(r["decisions"] for r in rows),
    }


def audit(baselines: list[dict], candidates: list[dict], training_seeds: set[int] | None = None) -> dict:
    baseline = index_arm(baselines, "baseline")
    candidate = index_arm(candidates, "model")
    if baseline.keys() != candidate.keys():
        raise ValueError("Unpaired seed sets")
    seeds = sorted(baseline)
    if training_seeds is not None and any(s in training_seeds for s in seeds):
        raise ValueError("Training/evaluation seed leakage")
    for s in seeds:
        a, b = baseline[s], candidate[s]
        if a["git_sha"] != b["git_sha"]:
            raise ValueError("Different game/evaluation source commits within seed pair")
        if a["agent_id"] != b["agent_id"]:
            raise ValueError("Different agent configuration within seed pair")
    weights = {candidate[s]["model_sha256"] for s in seeds}
    if len(weights) != 1:
        raise ValueError("Multiple model weights mixed in one candidate arm")
    base_rows = [baseline[s] for s in seeds]
    model_rows = [candidate[s] for s in seeds]
    deltas = [candidate[s]["placements"][0] - baseline[s]["placements"][0] for s in seeds]
    intervention_fields = {"forced_end_turns", "baseline_fallback_actions", "fallback_actions", "illegal_actions"}
    have_explicit_counters = all(intervention_fields <= set(x) for x in base_rows + model_rows)
    return {
        "schema": 1, "source": "paired schema-1 TavernGym receipts", "engine": ENGINE[1:],
        "seeds": seeds, "seat": 0, "pairs": len(seeds),
        "source_commits_by_seed": {str(s): baseline[s]["git_sha"] for s in seeds},
        "model_sha256": next(iter(weights)),
        "baseline": arm_stats(base_rows), "candidate": arm_stats(model_rows),
        "paired_rank_delta_candidate_minus_baseline": statistics.mean(deltas),
        "paired_delta_by_seed": deltas,
        "paired_delta_standard_error": statistics.stdev(deltas) / math.sqrt(len(deltas)) if len(deltas) > 1 else None,
        "uncertainty_note": "Small/seat-fixed sample: descriptive only; Wilson top4 intervals do not establish paired superiority.",
        "training_seed_disjointness": "verified_against_supplied_set" if training_seeds is not None else "unknown_not_supplied",
        "fallback_and_illegal_action_counters": "explicit_all_zero" if have_explicit_counters else "unknown_schema1_omits_counters",
        "raw_unassisted_model_performance_established": have_explicit_counters,
        "champion_promotion_authorized": False,
        "model_training_steps_in_this_audit": 0,
        "actual_games_played_in_this_audit": 0,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline", type=Path, nargs="+", required=True)
    p.add_argument("--candidate", type=Path, nargs="+", required=True)
    p.add_argument("--training-seeds", type=int, nargs="*")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    def read(paths: list[Path]) -> list[dict]:
        return [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    report = audit(read(args.baseline), read(args.candidate),
                   set(args.training_seeds) if args.training_seeds is not None else None)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
