"""Fail-closed paired TavernGym receipt audit. This never promotes models.

Designed as an opt-in companion to the existing evaluator. It does NOT
produce real matches or infer that model actions were safe from game results.
Guarded policies require explicit per-match fallback telemetry.
"""
from __future__ import annotations
import argparse
import json
import random
import re
import statistics
from pathlib import Path

ENGINE_HASH = "6d8712c93022ba11"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def verify(receipt: dict, *, seat: int, mode: str, fallback_count: int) -> dict:
    if not isinstance(receipt, dict) or receipt.get("schema") != 1:
        raise ValueError("Expected a canonical schema-1 match receipt")
    if type(seat) is not int or not 0 <= seat < 8:
        raise ValueError("Controlled seat must be 0..7")
    if mode not in ("raw", "guarded") or type(fallback_count) is not int or fallback_count < 0:
        raise ValueError("Invalid inference mode or fallback count")
    if mode == "raw" and fallback_count:
        raise ValueError("Raw-policy report cannot include fallback actions")
    if (receipt.get("environment"), receipt.get("engine_version"),
            receipt.get("engine_source_hash")) != ("TavernGym", "1.1.0", ENGINE_HASH):
        raise ValueError("Incompatible TavernGym version or source fingerprint")
    if receipt.get("completed") is not True or receipt.get("turn_limit_end") is not False:
        raise ValueError("Incomplete or forced-terminated match")
    if type(receipt.get("truncated_combats")) is not int or receipt["truncated_combats"] != 0:
        raise ValueError("Truncated or unverified combat")
    if type(receipt.get("seed")) is not int or receipt["seed"] < 0:
        raise ValueError("Invalid independent game seed")
    ranks = receipt.get("placements")
    if (not isinstance(ranks, list) or len(ranks) != 8
            or any(type(x) is not int for x in ranks)
            or sorted(ranks) != list(range(1, 9))):
        raise ValueError("Eight placements must form a permutation of 1..8")
    if type(receipt.get("decisions")) is not int or receipt["decisions"] < 1:
        raise ValueError("Invalid decision count")
    if receipt.get("policy") not in ("model", "baseline"):
        raise ValueError("Unrecognized controller policy")
    digest = receipt.get("model_sha256")
    if receipt["policy"] == "model":
        if not isinstance(digest, str) or not HEX64.fullmatch(digest):
            raise ValueError("Model receipt must identify exact checkpoint SHA256")
    elif digest is not None:
        raise ValueError("Baseline receipt cannot claim a model checksum")
    if mode == "guarded" and receipt["policy"] != "model":
        raise ValueError("Guarded baseline is not supported")
    return {"seed": receipt["seed"], "rank": ranks[seat], "policy": receipt["policy"],
            "model_sha256": digest, "decisions": receipt["decisions"]}


def compare(baseline: list[dict], candidate: list[dict], *, seats: list[int],
            baseline_mode: str = "raw", candidate_mode: str = "raw",
            baseline_fallbacks: list[int] | None = None,
            candidate_fallbacks: list[int] | None = None) -> dict:
    n = len(baseline)
    if not n or len(candidate) != n or len(seats) != n:
        raise ValueError("Paired receipts and explicit seats must have equal nonzero lengths")
    if baseline_mode == "guarded" and baseline_fallbacks is None:
        raise ValueError("Guarded baseline requires per-match fallback telemetry")
    if candidate_mode == "guarded" and candidate_fallbacks is None:
        raise ValueError("Guarded candidate requires per-match fallback telemetry")
    baseline_fallbacks = [0] * n if baseline_fallbacks is None else baseline_fallbacks
    candidate_fallbacks = [0] * n if candidate_fallbacks is None else candidate_fallbacks
    if len(baseline_fallbacks) != n or len(candidate_fallbacks) != n:
        raise ValueError("Per-match fallback telemetry length mismatch")
    rows, used = [], set()
    for bsrc, csrc, seat, bfb, cfb in zip(
            baseline, candidate, seats, baseline_fallbacks, candidate_fallbacks):
        b = verify(bsrc, seat=seat, mode=baseline_mode, fallback_count=bfb)
        c = verify(csrc, seat=seat, mode=candidate_mode, fallback_count=cfb)
        if b["seed"] != c["seed"]:
            raise ValueError("Seed mismatch invalidates paired comparison")
        key = (b["seed"], seat)
        if key in used:
            raise ValueError("Duplicate seed-seat pair")
        used.add(key)
        rows.append({
            "seed": b["seed"], "controlled_seat": seat,
            "baseline_rank": b["rank"], "candidate_rank": c["rank"],
            "delta_candidate_minus_baseline": c["rank"] - b["rank"],
            "baseline_controller": b["policy"], "candidate_controller": c["policy"],
            "baseline_checkpoint_sha256": b["model_sha256"],
            "candidate_checkpoint_sha256": c["model_sha256"],
            "baseline_fallback_count": bfb, "candidate_fallback_count": cfb,
        })
    deltas = [x["delta_candidate_minus_baseline"] for x in rows]
    interval = None
    if n >= 10:
        # Paired bootstrap is descriptive; it cannot establish model promotion.
        rng = random.Random(0)
        estimates = sorted(statistics.mean(rng.choices(deltas, k=n)) for _ in range(4000))
        interval = [estimates[99], estimates[3899]]
    return {
        "schema": 1, "method": "same_engine_seed_seat_paired",
        "games_per_policy": n,
        "baseline_mode": baseline_mode, "candidate_mode": candidate_mode,
        "fallback_telemetry": "caller_supplied_not_independently_attested",
        "baseline_mean_rank": statistics.mean(r["baseline_rank"] for r in rows),
        "candidate_mean_rank": statistics.mean(r["candidate_rank"] for r in rows),
        "baseline_top4_rate": sum(r["baseline_rank"] <= 4 for r in rows) / n,
        "candidate_top4_rate": sum(r["candidate_rank"] <= 4 for r in rows) / n,
        "baseline_first_rate": sum(r["baseline_rank"] == 1 for r in rows) / n,
        "candidate_first_rate": sum(r["candidate_rank"] == 1 for r in rows) / n,
        "mean_delta_candidate_minus_baseline": statistics.mean(deltas),
        "bootstrap_95pct_interval_if_n_at_least_10": interval,
        "limitations": "No CI for n<10; CI is descriptive. Game completion and masks "
                       "do not prove a raw model is useful. This tool never promotes Champion.",
        "champion_promoted": False, "pairs": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, nargs="+", required=True)
    parser.add_argument("--candidate", type=Path, nargs="+", required=True)
    parser.add_argument("--seats", required=True, help="Explicit controlled seat for every pair; e.g. 0,0,2")
    parser.add_argument("--baseline-mode", choices=("raw", "guarded"), default="raw")
    parser.add_argument("--candidate-mode", choices=("raw", "guarded"), default="raw")
    parser.add_argument("--baseline-fallbacks")
    parser.add_argument("--candidate-fallbacks")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    parse_counts = lambda s: [int(x) for x in s.split(",")] if s is not None else None
    read = lambda paths: [json.loads(x.read_text(encoding="utf-8")) for x in paths]
    result = compare(
        read(args.baseline), read(args.candidate), seats=parse_counts(args.seats),
        baseline_mode=args.baseline_mode, candidate_mode=args.candidate_mode,
        baseline_fallbacks=parse_counts(args.baseline_fallbacks),
        candidate_fallbacks=parse_counts(args.candidate_fallbacks))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "pairs"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
