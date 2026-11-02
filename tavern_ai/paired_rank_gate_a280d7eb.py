"""Strict, read-only paired evaluation of authentic eight-seat TavernGym receipts.

No simulator play is fabricated here: inputs must be completed game receipts.
This is a descriptive research gate, NOT a Champion promotion mechanism.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

from .receipt_integrity import validate_integrity

ENGINE = "6d8712c93022ba11"


def _seat(receipt: dict) -> int:
    values = [receipt[key] for key in ("controlled_seat", "seat") if key in receipt]
    if values and (len(set(map(str, values))) != 1):
        raise ValueError("Conflicting controlled seat labels")
    seat = values[0] if values else 0  # canary.py controls seat 0
    if type(seat) is not int or not 0 <= seat < 8:
        raise ValueError("Invalid controlled seat")
    return seat


def _check(rows: list[dict], policy: str) -> dict[tuple[int, int], dict]:
    if not rows:
        raise ValueError("At least one completed receipt is required")
    paired = {}
    for row in rows:
        validate_integrity(row)
        if row["policy"] != policy:
            raise ValueError("Raw model and baseline receipts must not be mixed")
        if row["engine_source_hash"] != ENGINE or row["engine_version"] != "1.1.0":
            raise ValueError("Engine contract mismatch")
        # model is a pure, unguarded action selector, not an assisted policy.
        if policy == "model" and (
            row.get("guarded") is True
            or row.get("raw_model_only") is False
            or any(row.get(k, 0) for k in
                   ("guard_forced_ends", "model_guard_forced_end", "fallback_count", "safety_fallbacks"))
        ):
            raise ValueError("Guarded or fallback-assisted model result cannot be treated as raw")
        key = (row["seed"], _seat(row))
        if key in paired:
            raise ValueError("Duplicate seed/seat evaluation receipt")
        paired[key] = row
    return paired


def summarize(candidate: list[dict], baseline: list[dict], *,
              bootstrap_samples: int = 2000) -> dict:
    """Lower placement is better. Same seed AND seat are required in both arms."""
    c = _check(candidate, "model")
    b = _check(baseline, "baseline")
    if set(c) != set(b):
        raise ValueError("Candidate/baseline seed-seat coverage differs")
    model_hashes = {r["model_sha256"] for r in c.values()}
    if len(model_hashes) != 1:
        raise ValueError("Different checkpoint hashes in one candidate comparison")
    if type(bootstrap_samples) is not int or bootstrap_samples < 100:
        raise ValueError("At least 100 bootstrap replicates required")
    keys = sorted(c)
    ranks_c = [c[k]["placements"][_seat(c[k])] for k in keys]
    ranks_b = [b[k]["placements"][_seat(b[k])] for k in keys]
    deltas = [x - y for x, y in zip(ranks_c, ranks_b)]
    rng = random.Random(20261102)
    means = sorted(statistics.mean(rng.choices(deltas, k=len(deltas)))
                   for _ in range(bootstrap_samples))
    low = means[int(0.025 * (len(means) - 1))]
    high = means[int(0.975 * (len(means) - 1))]
    return {
        "schema": 1,
        "engine_source_hash": ENGINE,
        "candidate_model_sha256": next(iter(model_hashes)),
        "paired_games": len(keys),
        "pairs": [{"seed": seed, "seat": seat, "model_rank": m, "baseline_rank": x,
                   "delta_model_minus_baseline": d}
                  for (seed, seat), m, x, d in zip(keys, ranks_c, ranks_b, deltas)],
        "model_mean_rank": statistics.mean(ranks_c),
        "baseline_mean_rank": statistics.mean(ranks_b),
        "model_first_rate": sum(x == 1 for x in ranks_c) / len(keys),
        "model_top4_rate": sum(x <= 4 for x in ranks_c) / len(keys),
        "baseline_first_rate": sum(x == 1 for x in ranks_b) / len(keys),
        "baseline_top4_rate": sum(x <= 4 for x in ranks_b) / len(keys),
        "paired_mean_rank_delta": statistics.mean(deltas),
        "bootstrap_95pct_descriptive_interval": [low, high],
        "strength_gain_proven": False,
        "promotion_allowed": False,
        "explanation": (
            "Descriptive seed/seat-matched results; small or correlated samples "
            "can invalidate bootstrap uncertainty. This tool NEVER promotes a model."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-receipts", nargs="+", type=Path, required=True)
    parser.add_argument("--baseline-receipts", nargs="+", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    load = lambda paths: [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    report = summarize(load(args.model_receipts), load(args.baseline_receipts))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"paired_games": report["paired_games"],
                      "paired_mean_rank_delta": report["paired_mean_rank_delta"],
                      "promotion_allowed": False}))


if __name__ == "__main__":
    main()
