"""Fail-closed paired full-game receipt evaluation; diagnostic only, never promotion.

This standalone V5 integration slice reuses canonical TavernGym receipt validation.
It cannot certify absence of model fallback when telemetry is missing.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from statistics import mean

from .validate_receipt import validate

_SHA = re.compile(r"[0-9a-f]{64}\Z")


def summarize_pairs(model_receipts: list[dict], baseline_receipts: list[dict],
                    registry: dict | None = None) -> dict:
    if not model_receipts or len(model_receipts) != len(baseline_receipts):
        raise ValueError("Nonempty, equally sized paired arms required")
    model_by_seed: dict[int, dict] = {}
    base_by_seed: dict[int, dict] = {}
    for rows, target, policy in (
        (model_receipts, model_by_seed, "model"),
        (baseline_receipts, base_by_seed, "baseline"),
    ):
        for row in rows:
            validate(row)
            if row.get("policy") != policy:
                raise ValueError("Policy arm mismatch")
            if sorted(row["placements"]) != list(range(1, 9)):
                raise ValueError("Placements must be a permutation of 1..8")
            seed = row.get("seed")
            if type(seed) is not int or seed < 0 or seed in target:
                raise ValueError("Invalid or duplicate seed")
            target[seed] = row
    if model_by_seed.keys() != base_by_seed.keys():
        raise ValueError("Unpaired model and baseline seeds")
    engine_fingerprints = {
        (r.get("engine_version"), r.get("engine_source_hash"))
        for r in model_receipts + baseline_receipts
    }
    if len(engine_fingerprints) != 1 or None in next(iter(engine_fingerprints)):
        raise ValueError("Mismatched/missing engine fingerprint")
    model_hashes = {r.get("model_sha256") for r in model_receipts}
    if len(model_hashes) != 1:
        raise ValueError("Mixed model checkpoint hashes")
    model_hash = next(iter(model_hashes))
    if not isinstance(model_hash, str) or not _SHA.fullmatch(model_hash):
        raise ValueError("Invalid model checkpoint SHA256")
    if any(r.get("model_sha256") is not None for r in baseline_receipts):
        raise ValueError("Baseline must not have model weights")
    if registry is not None:
        engine = registry.get("engine", {})
        observed_version, observed_source_hash = next(iter(engine_fingerprints))
        if (engine.get("version"), engine.get("source_hash")) != (
            observed_version, observed_source_hash
        ):
            raise ValueError("Receipt engine differs from model registry")
        if not any(c.get("checkpoint_sha256") == model_hash
                   for c in registry.get("candidates", [])):
            raise ValueError("Model digest absent from canonical registry")
    paired = [
        {"seed": seed, "model_rank": model_by_seed[seed]["placements"][0],
         "baseline_rank": base_by_seed[seed]["placements"][0],
         "model_minus_baseline": (model_by_seed[seed]["placements"][0]
                                  - base_by_seed[seed]["placements"][0])}
        for seed in sorted(model_by_seed)
    ]
    model_ranks = [row["model_rank"] for row in paired]
    base_ranks = [row["baseline_rank"] for row in paired]
    fallback_field = "safety_fallback_count"
    guard_telemetry_complete = all(fallback_field in r for r in model_receipts)
    any_guard = any(r.get(fallback_field, 0) != 0 for r in model_receipts)
    return {
        "schema": 1,
        "games_per_arm": len(paired),
        "model_sha256": model_hash,
        "engine": {"version": next(iter(engine_fingerprints))[0],
                   "source_hash": next(iter(engine_fingerprints))[1]},
        "pairs": paired,
        "model_mean_rank": mean(model_ranks),
        "baseline_mean_rank": mean(base_ranks),
        "mean_paired_rank_delta": mean(p["model_minus_baseline"] for p in paired),
        "model_top4_rate": sum(r <= 4 for r in model_ranks) / len(model_ranks),
        "model_first_rate": sum(r == 1 for r in model_ranks) / len(model_ranks),
        "fallback_telemetry_complete": guard_telemetry_complete,
        "fallback_reported": any_guard,
        "pure_model_play_verified": guard_telemetry_complete and not any_guard,
        "promotion_eligible": False,
        "inference": ("Descriptive paired full-game evidence only; no confidence "
                      "or causal claim, promotion needs independent review and "
                      "complete action/fallback telemetry."),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path, nargs="+", required=True)
    p.add_argument("--baseline", type=Path, nargs="+", required=True)
    p.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    load = lambda path: json.loads(path.read_text(encoding="utf-8"))
    summary = summarize_pairs([load(x) for x in args.model],
                              [load(x) for x in args.baseline], load(args.registry))
    encoded = json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()
