"""Fail-closed paired full-game evidence gate for V5 model evaluation.

Only reads genuine JSON receipts. A statistically favorable comparison is not
a promotion, and guarded/fallback completions remain diagnostic evidence.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from .receipt_integrity import validate_integrity
from .validate_receipt import validate as validate_legacy

ENGINE_HASH = "6d8712c93022ba11"


def _guard_count(row: dict) -> int:
    raw = row.get("opportunity_diagnostics", {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("Malformed opportunity diagnostics")
    counts = raw.get("counts", {})
    if not isinstance(counts, dict):
        raise ValueError("Malformed action counts")
    fields = (
        row.get("guard_forced_end", 0),
        row.get("guard_forced_ends", 0),
        row.get("forced_end_count", 0),
        row.get("fallback_count", 0),
        row.get("fallback_actions", 0),
        row.get("safety_fallback_count", 0),
        counts.get("guard_forced_end", 0),
        counts.get("guard_forced_ends", 0),
        counts.get("fallback_actions", 0),
    )
    if any(type(v) is not int or v < 0 for v in fields):
        raise ValueError("Invalid guard/fallback counter")
    return max(fields)


def _checked(row: dict, arm: str) -> tuple[tuple[int, int], int, bool]:
    if not isinstance(row, dict):
        raise ValueError("Receipt must be an object")
    policy = row.get("policy")
    guarded = policy == "model_guarded" or row.get("guarded") is True
    n_guard = _guard_count(row)
    if arm == "baseline":
        if policy != "baseline" or guarded or n_guard:
            raise ValueError("Baseline receipt must be an unguarded baseline")
        validate_integrity(row)
    elif arm == "candidate":
        if policy not in ("model", "model_guarded"):
            raise ValueError("Candidate must identify model policy")
        if not guarded and n_guard:
            raise ValueError("Undisclosed guard/fallback in raw model receipt")
        if not guarded:
            validate_integrity(row)
        else:
            validate_legacy(row)
            import re
            if re.fullmatch(r"[0-9a-f]{64}", str(row.get("model_sha256", ""))) is None:
                raise ValueError("Guarded model needs a real model SHA256")
    else:
        raise ValueError("Unknown arm")
    if row.get("engine_version") != "1.1.0" or row.get("engine_source_hash") != ENGINE_HASH:
        raise ValueError("Unpinned TavernGym version/fingerprint")
    if sorted(row["placements"]) != list(range(1, 9)):
        raise ValueError("Placement is not a permutation of 1..8")
    seat = row.get("seat", 0)
    seed = row.get("seed")
    if type(seat) is not int or not 0 <= seat < 8:
        raise ValueError("Invalid controlled seat")
    if type(seed) is not int or seed < 0:
        raise ValueError("Invalid seed")
    rank = row["placements"][seat]
    if "agent_placement" in row and row["agent_placement"] != rank:
        raise ValueError("Seat/rank mismatch")
    if row.get("turn_limit_end") is not False or row.get("truncated_combats") != 0:
        raise ValueError("Simulator guard or truncated combat")
    return (seed, seat), rank, guarded


def _index(rows: list[dict], arm: str) -> dict[tuple[int, int], tuple[int, bool]]:
    if not isinstance(rows, list) or not rows:
        raise ValueError("Require nonempty receipt list")
    out = {}
    hashes = set()
    for row in rows:
        key, rank, guarded = _checked(row, arm)
        if key in out:
            raise ValueError("Duplicate seed/seat; not independent pairs")
        out[key] = (rank, guarded)
        if arm == "candidate":
            hashes.add(row["model_sha256"])
    if arm == "candidate" and len(hashes) != 1:
        raise ValueError("Candidate model SHA changes across games")
    return out


def _percentile(sorted_values: list[float], q: float) -> float:
    index = (len(sorted_values) - 1) * q
    lower = math.floor(index)
    upper = math.ceil(index)
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * (index - lower)


def compare(candidate: list[dict], baseline: list[dict], *, draws: int = 4000) -> dict:
    if type(draws) is not int or not 100 <= draws <= 20000:
        raise ValueError("draws must be between 100 and 20000")
    c = _index(candidate, "candidate")
    b = _index(baseline, "baseline")
    if c.keys() != b.keys():
        raise ValueError("Candidate and baseline must have identical seed/seat pairs")
    keys = sorted(c)
    diffs = [c[k][0] - b[k][0] for k in keys]  # negative favors candidate
    n = len(keys)
    guarded = sum(c[k][1] for k in keys)
    delta = sum(diffs) / n
    ci = None
    if n >= 5:
        rng = random.Random(20261102)
        samples = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(draws))
        ci = [_percentile(samples, 0.025), _percentile(samples, 0.975)]
    status = "diagnostic_guarded_not_promotable" if guarded else "insufficient_evidence"
    if not guarded and n >= 20 and ci is not None and ci[1] < 0:
        status = "statistical_signal_only_requires_independent_promotion_review"
    return {
        "schema": 1,
        "source": "paired full eight-seat TavernGym receipts",
        "seed_seat_pairs": [{"seed": seed, "seat": seat} for seed, seat in keys],
        "games_per_arm": n,
        "candidate_placements": [c[k][0] for k in keys],
        "baseline_placements": [b[k][0] for k in keys],
        "candidate_mean_placement": sum(c[k][0] for k in keys) / n,
        "baseline_mean_placement": sum(b[k][0] for k in keys) / n,
        "candidate_top4_rate": sum(c[k][0] <= 4 for k in keys) / n,
        "candidate_first_place_rate": sum(c[k][0] == 1 for k in keys) / n,
        "paired_differences_candidate_minus_baseline": diffs,
        "paired_mean_placement_delta": delta,
        "paired_bootstrap_95pct_interval": ci,
        "guarded_candidate_games": guarded,
        "pure_model_candidate_games": n - guarded,
        "model_promotion_authorized": False,
        "evidence_status": status,
        "limitations": "No training/heldout seed overlap test; bootstrap measures paired seed variation only, not causality. Guarded games never prove raw policy strength.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate", type=Path, required=True, help="JSON list of real model receipts")
    p.add_argument("--baseline", type=Path, required=True, help="JSON list of same-seed baseline receipts")
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    report = compare(
        json.loads(a.candidate.read_text(encoding="utf-8")),
        json.loads(a.baseline.read_text(encoding="utf-8")),
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
