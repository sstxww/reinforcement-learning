"""Strict, non-intervening comparison of real eight-seat TavernGym receipts.

This gate audits *existing* finished matches. It never trains a model, modifies
an action, or promotes a checkpoint. It rejects guarded model outcomes.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from pathlib import Path

from .contract import ENGINE_HASH
from .validate_receipt import validate

_SHA256 = re.compile(r"[a-f0-9]{64}\Z")
_T_CRIT_95 = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776,
              6: 2.571, 7: 2.447, 8: 2.365, 9: 2.306,
              10: 2.262, 11: 2.228, 12: 2.201}


def _audit(rows: list[dict], expected_policy: str) -> dict[int, dict]:
    if not rows:
        raise ValueError(f"No {expected_policy} receipts")
    by_seed: dict[int, dict] = {}
    model_hashes: set[str] = set()
    for r in rows:
        if not isinstance(r, dict):
            raise ValueError("Receipt must be an object")
        validate(r)
        if r.get("policy") != expected_policy:
            raise ValueError("A guarded or mismatched policy is not a raw model/baseline")
        if sorted(r["placements"]) != list(range(1, 9)):
            raise ValueError("Final placements are not a permutation of 1..8")
        if r.get("engine_version") != "1.1.0" or r.get("engine_source_hash") != ENGINE_HASH:
            raise ValueError("TavernGym version/hash mismatch")
        # Current canonical canary always controls seat 0. Rotated seats require
        # an explicit separate protocol, not implicit placements[0].
        if r.get("seat", 0) != 0:
            raise ValueError("Nonzero seat requires explicit seat-rotation protocol")
        if r.get("guard_forced_ends", 0) or r.get("fallback_count", 0) or r.get("safety_fallback_count", 0):
            raise ValueError("Safety fallback contaminates raw policy performance")
        if r.get("raw_model_only") is False:
            raise ValueError("Assisted policy cannot be treated as raw model")
        seed = r.get("seed")
        if type(seed) is not int or seed < 0 or seed in by_seed:
            raise ValueError("Missing, invalid or duplicate evaluation seed")
        digest = r.get("model_sha256")
        if expected_policy == "model":
            if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
                raise ValueError("Missing valid model weight digest")
            model_hashes.add(digest)
        elif digest is not None:
            raise ValueError("Baseline receipt unexpectedly names model weights")
        by_seed[seed] = r
    if len(model_hashes) > 1:
        raise ValueError("Different candidate model weights mixed in one comparison")
    return by_seed


def _summary(rows: dict[int, dict]) -> dict:
    ranks = [rows[s]["placements"][0] for s in sorted(rows)]
    return {"games": len(ranks), "mean_rank": statistics.mean(ranks),
            "top4_rate": sum(rank <= 4 for rank in ranks) / len(ranks),
            "first_rate": sum(rank == 1 for rank in ranks) / len(ranks),
            "ranks": ranks}


def _paired_ci95(deltas: list[int]) -> list[float] | None:
    """Approximate two-sided Student-t interval; not a promotion threshold."""
    n = len(deltas)
    if n < 2:
        return None
    t = _T_CRIT_95.get(n, 2.0 if n > 12 else None)
    if t is None:
        return None
    center = statistics.mean(deltas)
    margin = t * statistics.stdev(deltas) / math.sqrt(n)
    return [center - margin, center + margin]


def compare(candidate: list[dict], baseline: list[dict]) -> dict:
    c = _audit(candidate, "model")
    b = _audit(baseline, "baseline")
    if c.keys() != b.keys():
        raise ValueError("Candidate/baseline seeds are not exactly paired")
    seeds = sorted(c)
    deltas = [c[s]["placements"][0] - b[s]["placements"][0] for s in seeds]
    return {
        "schema": 1, "source": "validated_eight_seat_receipts",
        "engine_version": "1.1.0", "engine_source_hash": ENGINE_HASH,
        "controlled_seat": 0, "seeds": seeds,
        "candidate_model_sha256": c[seeds[0]]["model_sha256"],
        "candidate": _summary(c), "baseline": _summary(b),
        "candidate_minus_baseline_rank_deltas": deltas,
        "mean_rank_delta": statistics.mean(deltas),
        "approx_t_ci95": _paired_ci95(deltas),
        "raw_model_only": True, "fallback_count": 0,
        "champion_promotion_eligible": False,
        "caveat": "Retrospective paired receipt audit, no new games or PPO training. "
                  "Small-sample t interval is descriptive, not causal or proof of competitive gain."
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate", type=Path, nargs="+", required=True)
    p.add_argument("--baseline", type=Path, nargs="+", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    c = [json.loads(x.read_text(encoding="utf-8")) for x in a.candidate]
    b = [json.loads(x.read_text(encoding="utf-8")) for x in a.baseline]
    result = compare(c, b)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
