"""Read-only, fail-closed paired V5 full-game evidence screen.

This module never promotes a model, trains a model, or creates match receipts.
It compares existing genuine TavernGym receipts; confidence is exploratory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import statistics
from pathlib import Path

from .validate_receipt import validate

ENGINE_HASH = "6d8712c93022ba11"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def _read(path: Path, policy: str) -> dict:
    record = json.loads(path.read_text(encoding="utf-8"))
    validate(record)
    if sorted(record["placements"]) != list(range(1, 9)):
        raise ValueError(f"Invalid placement permutation: {path}")
    if record.get("policy") != policy:
        raise ValueError(f"Incorrect policy in {path}")
    if record.get("engine_version") != "1.1.0" or record.get("engine_source_hash") != ENGINE_HASH:
        raise ValueError(f"Incompatible TavernGym version in {path}")
    if type(record.get("seed")) is not int or record["seed"] < 0:
        raise ValueError(f"Invalid seed in {path}")
    seat = record.get("seat", 0)
    if type(seat) is not int or not 0 <= seat < 8:
        raise ValueError(f"Invalid controlled seat in {path}")
    record["_seat"] = seat
    record["_rank"] = record["placements"][seat]
    if policy == "model":
        digest = record.get("model_sha256")
        if not isinstance(digest, str) or not HEX64.fullmatch(digest):
            raise ValueError(f"Model SHA256 missing in {path}")
        if record.get("safety_fallback_count", 0) not in (0, None) or record.get("model_guard_forced_end", 0) not in (0, None):
            raise ValueError(f"Guarded model evidence cannot be scored as raw: {path}")
    else:
        if record.get("model_sha256") is not None:
            raise ValueError(f"Baseline receipt contains model checkpoint in {path}")
    return record


def _by_key(paths: list[Path], policy: str) -> dict:
    indexed = {}
    if not paths:
        raise ValueError(f"Missing {policy} receipts")
    for path in paths:
        row = _read(path, policy)
        key = (row["seed"], row["_seat"])
        if key in indexed:
            raise ValueError(f"Repeated {policy} seed/seat: {key}")
        indexed[key] = row
    return indexed


def _bootstrap_interval(deltas: list[int]) -> list[float] | None:
    if len(deltas) < 2:
        return None
    rng = random.Random(20261102)
    means = sorted(statistics.mean(rng.choices(deltas, k=len(deltas))) for _ in range(4000))
    return [means[99], means[3899]]  # 2.5th and 97.5th percentiles


def compare(model_paths: list[Path], baseline_paths: list[Path]) -> dict:
    model = _by_key(model_paths, "model")
    baseline = _by_key(baseline_paths, "baseline")
    if set(model) != set(baseline):
        raise ValueError("Unpaired seeds/seats; never silently drop missing games")
    hashes = {r["model_sha256"] for r in model.values()}
    if len(hashes) != 1:
        raise ValueError("Mixed model weights in one candidate evaluation")
    keys = sorted(model)
    deltas = [model[k]["_rank"] - baseline[k]["_rank"] for k in keys]
    candidates = [model[k]["_rank"] for k in keys]
    references = [baseline[k]["_rank"] for k in keys]
    ci = _bootstrap_interval(deltas)
    disclosed = all(
        "safety_fallback_count" in r or "model_guard_forced_end" in r
        for r in model.values()
    )
    # This is only a statistical screen; promotion also requires independent
    # checkpoint, optimizer, CI and integration checks.
    screen = len(keys) >= 30 and ci is not None and ci[1] < 0 and disclosed
    return {
        "schema": 1,
        "type": "descriptive_paired_full_game_screen",
        "games_per_arm": len(keys),
        "pairs": [{"seed": seed, "seat": seat, "model_rank": model[(seed, seat)]["_rank"],
                   "baseline_rank": baseline[(seed, seat)]["_rank"]}
                  for seed, seat in keys],
        "model_sha256": next(iter(hashes)),
        "model_mean_placement": statistics.mean(candidates),
        "baseline_mean_placement": statistics.mean(references),
        "paired_mean_placement_delta": statistics.mean(deltas),
        "paired_bootstrap_95_interval": ci,
        "model_top4_rate": sum(p <= 4 for p in candidates) / len(keys),
        "baseline_top4_rate": sum(p <= 4 for p in references) / len(keys),
        "model_first_place_rate": sum(p == 1 for p in candidates) / len(keys),
        "baseline_first_place_rate": sum(p == 1 for p in references) / len(keys),
        "fallback_disclosure_complete": disclosed,
        "statistical_screen_passed_for_human_review": bool(screen),
        "champion_promoted": False,
        "caveat": "Exploratory percentile bootstrap; seeds and seats must be paired. No strength or Champion claim from this summary.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-receipts", type=Path, nargs="+", required=True)
    parser.add_argument("--baseline-receipts", type=Path, nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = compare(args.model_receipts, args.baseline_receipts)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
