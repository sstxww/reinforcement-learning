"""V5 fail-closed paired evaluation of already-existing authentic match receipts.

This is a read-only evidence gate: never launches games, trains, changes weights,
or promotes a Champion. Assisted results are deliberately NOT raw-model results.
Positive mean rank delta means the candidate is worse than baseline.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

from .receipt_integrity import validate_integrity

SESSION_ID = "s-20261102-f25a91c8"


def _verified(rows: list[dict], policy: str) -> dict[tuple[int, int], dict]:
    if not isinstance(rows, list) or not rows:
        raise ValueError("At least one authentic receipt per arm is required")
    result: dict[tuple[int, int], dict] = {}
    for receipt in rows:
        if not isinstance(receipt, dict):
            raise ValueError("Receipt must be an object")
        # Do not recast model_guarded / fallback models as pure model games,
        # even when a specific game happened to invoke no forced actions.
        if receipt.get("policy") != policy:
            raise ValueError("Assisted/incorrect policy cannot enter raw-model comparison")
        validate_integrity(receipt)
        if receipt.get("guarded") is True or receipt.get("raw_model_only") is False:
            raise ValueError("Guarded or fallback-assisted match cannot be raw evidence")
        for field in ("guard_forced_ends", "safety_fallbacks", "fallback_count"):
            n = receipt.get(field, 0)
            if type(n) is not int or n != 0:
                raise ValueError(f"Nonzero or invalid assistance counter: {field}")
        if receipt.get("truncated_combats") != 0 or receipt.get("turn_limit_end") is not False:
            raise ValueError("Simulator or turn safety fallback contaminates result")
        seat = receipt.get("seat", 0)
        if type(seat) is not int or not 0 <= seat <= 7:
            raise ValueError("Missing valid controlled seat")
        key = (receipt["seed"], seat)
        if key in result:
            raise ValueError(f"Duplicate seed/seat comparison: {key}")
        result[key] = receipt
    return result


def _metrics(placements: list[int]) -> dict:
    return {
        "games": len(placements),
        "mean_placement": statistics.mean(placements),
        "top4_rate": sum(r <= 4 for r in placements) / len(placements),
        "first_place_rate": sum(r == 1 for r in placements) / len(placements),
        "placements": placements,
    }


def evaluate_pairs(candidate: list[dict], baseline: list[dict], *, bootstrap_draws: int = 2000) -> dict:
    if type(bootstrap_draws) is not int or not 100 <= bootstrap_draws <= 10000:
        raise ValueError("bootstrap_draws must be 100..10000")
    c = _verified(candidate, "model")
    b = _verified(baseline, "baseline")
    if c.keys() != b.keys() or len(c) < 2:
        raise ValueError("Need at least two exactly matched (seed, seat) pairs")
    hashes = {r["model_sha256"] for r in c.values()}
    if len(hashes) != 1:
        raise ValueError("Comparison mixes multiple checkpoint hashes")
    keys = sorted(c)
    cand = [c[k]["placements"][k[1]] for k in keys]
    base = [b[k]["placements"][k[1]] for k in keys]
    deltas = [x - y for x, y in zip(cand, base)]
    rng = random.Random(20261102)
    means = sorted(statistics.mean(rng.choices(deltas, k=len(deltas)))
                   for _ in range(bootstrap_draws))
    low = means[int(0.025 * (bootstrap_draws - 1))]
    high = means[int(0.975 * (bootstrap_draws - 1))]
    return {
        "schema": 1,
        "session_id": SESSION_ID,
        "policy_scope": "raw_unassisted_paired_full_games_only",
        "source": "provided_receipt_files_verified_not_new_games",
        "model_sha256": next(iter(hashes)),
        "pairs": len(keys),
        "seed_seat_pairs": [{"seed": seed, "seat": seat} for seed, seat in keys],
        "candidate": _metrics(cand),
        "baseline": _metrics(base),
        "paired_rank_deltas": deltas,
        "paired_mean_placement_delta": statistics.mean(deltas),
        "paired_bootstrap_95pct_interval": [low, high],
        "paired_bootstrap_draws": bootstrap_draws,
        "direction": "negative candidate-minus-baseline is better",
        "signal_for_manual_review_only": len(keys) >= 16 and high < 0,
        "champion_promoted": False,
        "warning": "Same seeds are paired observations, not causal control for all engine randomness. Bootstrap uncertainty is descriptive; no automatic promotion.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate", type=Path, nargs="+", required=True)
    p.add_argument("--baseline", type=Path, nargs="+", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    c = [json.loads(path.read_text(encoding="utf-8")) for path in a.candidate]
    b = [json.loads(path.read_text(encoding="utf-8")) for path in a.baseline]
    result = evaluate_pairs(c, b)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
