"""Fail-closed paired full-game evidence audit (no automatic model promotion).

This is a read-only adapter over the project's canonical receipt-integrity
checker. It prevents rescued/guarded PPO matches from being compared as raw
model results. Synthetic unit-test fixtures are NOT real games.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from .receipt_integrity import validate_integrity


def _cohort(rows: list[dict], kind: str) -> dict[tuple[int, int], dict]:
    if not rows:
        raise ValueError(f"No {kind} game receipts")
    indexed = {}
    digest = None
    for receipt in rows:
        validate_integrity(receipt)
        if receipt["policy"] != kind:
            raise ValueError(f"{kind} arm contains an unexpected policy")
        seat = receipt.get("controlled_seat", 0)
        if type(seat) is not int or not 0 <= seat < 8:
            raise ValueError("Invalid controlled seat")
        key = (receipt["seed"], seat)
        if key in indexed:
            raise ValueError(f"Duplicate {kind} seed/seat pair: {key}")
        if kind == "model":
            sha = receipt["model_sha256"]
            if digest is None:
                digest = sha
            if digest != sha:
                raise ValueError("Candidate arm mixes different checkpoints")
            guard = (
                receipt.get("guard_interventions", 0),
                receipt.get("safety_fallback_count", 0),
                receipt.get("forced_end_turns", 0),
                receipt.get("baseline_fallback_actions", 0),
            )
            if any(type(v) is not int or v < 0 for v in guard):
                raise ValueError("Invalid safety-intervention counter")
            if any(guard):
                raise ValueError("Guarded/model-rescued gameplay is not raw PPO evidence")
            if receipt.get("policy_variant", "raw_ppo_model") not in (
                "raw_ppo_model", "model_without_fallback"
            ):
                raise ValueError("Guarded or ambiguous model variant")
        indexed[key] = receipt
    return indexed


def audit_pair(baseline: list[dict], candidate: list[dict]) -> dict:
    """Compare strict real-game receipts; negative delta means model better."""
    b = _cohort(baseline, "baseline")
    c = _cohort(candidate, "model")
    if set(b) != set(c):
        raise ValueError("Missing or unequal heldout seed/seat pairs")
    keys = sorted(b)
    for key in keys:
        if (b[key]["engine_source_hash"] != c[key]["engine_source_hash"]
                or b[key]["engine_version"] != c[key]["engine_version"]):
            raise ValueError("Engine mismatch within paired evaluation")
    base_ranks = [b[k]["placements"][k[1]] for k in keys]
    cand_ranks = [c[k]["placements"][k[1]] for k in keys]
    deltas = [c - v for c, v in zip(cand_ranks, base_ranks)]
    n = len(keys)
    return {
        "schema": 1, "pairs": n, "complete_games": 2 * n,
        "model_sha256": c[keys[0]]["model_sha256"],
        "seeds_and_seats": [{"seed": s, "seat": seat} for s, seat in keys],
        "baseline_ranks": base_ranks, "candidate_ranks": cand_ranks,
        "paired_rank_delta_candidate_minus_baseline": statistics.mean(deltas),
        "sample_stdev_paired_delta": statistics.stdev(deltas) if n >= 2 else None,
        "candidate_top4_rate": sum(x <= 4 for x in cand_ranks) / n,
        "candidate_first_rate": sum(x == 1 for x in cand_ranks) / n,
        "baseline_top4_rate": sum(x <= 4 for x in base_ranks) / n,
        "baseline_first_rate": sum(x == 1 for x in base_ranks) / n,
        "guarded_or_fallback_games": 0,
        "promotion_eligible": False,
        "interpretation": "Descriptive paired evidence only; independent review and uncertainty analysis are required before promotion.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, nargs="+", required=True)
    parser.add_argument("--candidate", type=Path, nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    read = lambda paths: [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    report = audit_pair(read(args.baseline), read(args.candidate))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
