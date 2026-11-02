"""Fail-closed paired eight-seat TavernGym receipt statistics (no strength promotion).

Consumes *already completed* real game receipts. It never fabricates matches,
trains a policy, treats guarded play as raw PPO, or certifies a Champion.
"""
from __future__ import annotations

import argparse
import glob
import json
import random
import re
import statistics
from pathlib import Path

from .validate_receipt import validate

ENGINE_HASH = "6d8712c93022ba11"
SHA256 = re.compile(r"^[a-f0-9]{64}$")
CANDIDATE_POLICIES = {"model", "model_guarded", "guarded_model"}


def _index(rows: list[dict], role: str) -> dict[int, dict]:
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"No {role} receipts")
    indexed = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Receipt must be a JSON object")
        validate(row)
        if (row.get("engine_version") != "1.1.0"
                or row.get("engine_source_hash") != ENGINE_HASH):
            raise ValueError("Mismatched pinned TavernGym engine")
        if sorted(row["placements"]) != list(range(1, 9)):
            raise ValueError("Placements are not an eight-seat permutation")
        seed = row.get("seed")
        if type(seed) is not int or seed < 0 or seed in indexed:
            raise ValueError("Missing, invalid or duplicate match seed")
        policy = row.get("policy")
        if role == "baseline":
            if policy != "baseline" or row.get("model_sha256") is not None:
                raise ValueError("Baseline must be the unassisted rules policy")
        else:
            if policy not in CANDIDATE_POLICIES:
                raise ValueError("Candidate is not a model policy")
            if not isinstance(row.get("model_sha256"), str) or not SHA256.fullmatch(row["model_sha256"]):
                raise ValueError("Candidate model SHA256 is missing")
        indexed[seed] = row
    return indexed


def paired_summary(baseline: list[dict], candidate: list[dict]) -> dict:
    b = _index(baseline, "baseline")
    c = _index(candidate, "candidate")
    if b.keys() != c.keys():
        raise ValueError("Paired evaluation requires exactly matching independent seeds")
    ids = {row["model_sha256"] for row in c.values()}
    if len(ids) != 1:
        raise ValueError("Cannot mix checkpoints in a single comparison")
    seeds = sorted(b)
    br = [b[s]["placements"][0] for s in seeds]
    cr = [c[s]["placements"][0] for s in seeds]
    deltas = [x - y for x, y in zip(cr, br)]
    assisted = any(
        row["policy"] != "model" or row.get("guarded") is True
        or row.get("raw_model_only") is False
        or row.get("guard_forced_ends", row.get("forced_ends", 0)) != 0
        for row in c.values()
    )
    # Seeded percentile bootstrap of *paired* placement deltas. Very small
    # samples remain exploratory even when an interval excludes zero.
    rng = random.Random(0)
    resamples = [
        statistics.mean(rng.choices(deltas, k=len(deltas)))
        for _ in range(2048)
    ]
    resamples.sort()
    return {
        "schema": 1,
        "source": "complete_eight_seat_taverngym_receipts",
        "engine_source_hash": ENGINE_HASH,
        "candidate_sha256": next(iter(ids)),
        "policy_provenance": "guarded_or_assisted_model" if assisted else "raw_model",
        "seeds": seeds,
        "games_per_policy": len(seeds),
        "baseline": {"ranks": br, "mean_rank": statistics.mean(br),
                     "top4_rate": sum(rank <= 4 for rank in br) / len(br),
                     "first_place_rate": sum(rank == 1 for rank in br) / len(br)},
        "candidate": {"ranks": cr, "mean_rank": statistics.mean(cr),
                      "top4_rate": sum(rank <= 4 for rank in cr) / len(cr),
                      "first_place_rate": sum(rank == 1 for rank in cr) / len(cr)},
        "paired_rank_deltas_candidate_minus_baseline": deltas,
        "paired_mean_rank_delta": statistics.mean(deltas),
        "paired_delta_bootstrap_95pct_exploratory": [
            resamples[int(0.025 * (len(resamples) - 1))],
            resamples[int(0.975 * (len(resamples) - 1))],
        ],
        "promotion_eligible": False,
        "uncertainty_note": (
            "Decision/turn observations are correlated; bootstrap resamples whole "
            "matched games, not decisions. This descriptive tool does not establish "
            "causal improvement, independent train/test separation or Champion status."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline-glob", required=True)
    p.add_argument("--candidate-glob", required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    def read(pattern: str) -> list[dict]:
        paths = sorted(glob.glob(pattern))
        if not paths:
            raise ValueError(f"No receipts match: {pattern}")
        return [json.loads(Path(path).read_text(encoding="utf-8")) for path in paths]
    result = paired_summary(read(args.baseline_glob), read(args.candidate_glob))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
