"""Strict offline paired TavernGym receipt comparison (no model promotion).

Use on independent, same-engine, same-seat completed eight-player receipts.
A guarded policy stays explicitly labelled; this module never claims causality.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from pathlib import Path

from .validate_receipt import validate

_ENGINE_VERSION = "1.1.0"
_ENGINE_SOURCE_HASH = "6d8712c93022ba11"
_SHA256 = re.compile(r"[a-f0-9]{64}\Z")
_GUARD_KEYS = ("guard_interventions", "guard_forced_ends", "safety_fallback_count")


def _validated(record: dict, label: str) -> tuple[int, int, str]:
    """Return seed, controlled seat, and actual policy class (raw/guarded/baseline)."""
    if not isinstance(record, dict):
        raise ValueError(f"{label}: record must be an object")
    validate(record)
    if sorted(record["placements"]) != list(range(1, 9)):
        raise ValueError(f"{label}: placements must be a permutation of 1..8")
    if (record.get("engine_version") != _ENGINE_VERSION or
            record.get("engine_source_hash") != _ENGINE_SOURCE_HASH):
        raise ValueError(f"{label}: pinned TavernGym engine mismatch")
    seed, seat = record.get("seed"), record.get("controlled_seat", 0)
    if type(seed) is not int or seed < 0 or type(seat) is not int or not 0 <= seat < 8:
        raise ValueError(f"{label}: invalid seed or controlled seat")
    if record.get("policy") not in ("baseline", "model", "guarded_model", "model_guarded"):
        raise ValueError(f"{label}: unknown policy")
    for name in _GUARD_KEYS:
        value = record.get(name, 0)
        if type(value) is not int or value < 0:
            raise ValueError(f"{label}: invalid {name}")
    if record["policy"] == "baseline":
        if any(record.get(k, 0) for k in _GUARD_KEYS):
            raise ValueError(f"{label}: baseline unexpectedly used model guard")
        kind = "baseline"
    else:
        sha = record.get("model_sha256")
        if not isinstance(sha, str) or not _SHA256.fullmatch(sha):
            raise ValueError(f"{label}: model weight SHA256 is missing/invalid")
        variant = record.get("policy_variant")
        guarded = (record["policy"] in ("guarded_model", "model_guarded") or
                   record.get("guarded") is True or
                   any(record.get(k, 0) > 0 for k in _GUARD_KEYS) or
                   record.get("raw_model_only") is False or
                   (variant is not None and variant not in ("raw_ppo_model", "raw_model", "raw")))
        kind = "guarded_model" if guarded else "raw_model"
    return seed, seat, kind


def _map_records(records: list[dict], label: str) -> tuple[dict[tuple[int, int], dict], str]:
    if not isinstance(records, list) or not records or len(records) > 200:
        raise ValueError(f"{label}: require 1..200 game receipts")
    indexed: dict[tuple[int, int], dict] = {}
    kinds = set()
    for i, record in enumerate(records):
        seed, seat, kind = _validated(record, f"{label}[{i}]")
        key = (seed, seat)
        if key in indexed:
            raise ValueError(f"{label}: duplicate seed/seat {key}")
        indexed[key] = record
        kinds.add(kind)
    if len(kinds) != 1:
        raise ValueError(f"{label}: cannot mix raw and guarded policy results")
    return indexed, kinds.pop()


def _wilson(successes: int, total: int) -> list[float]:
    # 95% Wilson score interval. Descriptive uncertainty, NOT a rank-gain test.
    z = 1.959963984540054
    p = successes / total
    denom = 1 + z*z / total
    center = (p + z*z/(2*total)) / denom
    radius = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / denom
    return [max(0, center-radius), min(1, center+radius)]


def _summarize(rows: list[dict]) -> dict:
    ranks = [r["placements"][r.get("controlled_seat", 0)] for r in rows]
    top4 = sum(r <= 4 for r in ranks)
    wins = sum(r == 1 for r in ranks)
    return {
        "games": len(rows), "ranks": ranks,
        "mean_rank": statistics.mean(ranks),
        "top4_rate": top4 / len(rows), "top4_wilson95": _wilson(top4, len(rows)),
        "win_rate": wins / len(rows), "win_wilson95": _wilson(wins, len(rows)),
        "decisions": sum(r["decisions"] for r in rows),
        "guard_interventions_reported": sum(max(r.get(k, 0) for k in _GUARD_KEYS) for r in rows),
    }


def paired_report(candidate: list[dict], baseline: list[dict]) -> dict:
    cand, ck = _map_records(candidate, "candidate")
    base, bk = _map_records(baseline, "baseline")
    if bk != "baseline" or ck == "baseline":
        raise ValueError("Require genuine baseline arm and candidate model arm")
    if cand.keys() != base.keys():
        raise ValueError("Candidate and baseline must have identical seed/seat pairs")
    weights = {r["model_sha256"] for r in cand.values()}
    if len(weights) != 1:
        raise ValueError("Candidate arm mixes distinct model checkpoints")
    keys = sorted(cand)
    c, b = [cand[k] for k in keys], [base[k] for k in keys]
    deltas = [x["placements"][k[1]] - y["placements"][k[1]]
              for k, x, y in zip(keys, c, b)]
    return {
        "schema": 1, "engine_version": _ENGINE_VERSION,
        "engine_source_hash": _ENGINE_SOURCE_HASH,
        "candidate_kind": ck, "candidate_model_sha256_claim": next(iter(weights)),
        "checkpoint_bytes_verified_by_this_report": False,
        "paired_seed_seat": [{"seed": s, "seat": seat} for s, seat in keys],
        "candidate": _summarize(c), "baseline": _summarize(b),
        "paired_rank_deltas": deltas,
        "paired_mean_rank_delta": statistics.mean(deltas),
        "interpretation": "Lower mean rank is better. Complete-game receipt validation is not proof of model strength or checkpoint integrity.",
        "caveat": "Wilson intervals describe win/top4 rates; no causal or statistically significant rank gain is claimed. Samples and gameplay seeds must be independent of training.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", nargs="+", required=True, type=Path)
    parser.add_argument("--baseline", nargs="+", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    report = paired_report(
        [json.loads(p.read_text(encoding="utf-8")) for p in args.candidate],
        [json.loads(p.read_text(encoding="utf-8")) for p in args.baseline],
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
