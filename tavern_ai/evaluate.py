"""Seeded full-game evaluation with validated raw receipts and paired uncertainty.

One controlled seat versus seven simulator bots. This is NOT Arena Elo.
A model-vs-baseline comparison uses identical held-out seeds, and both arms
must be complete, unassisted, engine-compatible eight-seat games.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

from .canary import run
from .contract import ENGINE_HASH


def summarize(records: list[dict]) -> dict:
    if not records:
        raise ValueError("Cannot summarize zero games")
    placements = [r["placements"][0] for r in records]
    return {
        "games": len(records),
        "mean_placement": statistics.mean(placements),
        "top4_rate": sum(x <= 4 for x in placements) / len(records),
        "first_place_rate": sum(x == 1 for x in placements) / len(records),
        "placements": placements,
        "seeds": [r["seed"] for r in records],
    }


def validate_real_games(records: list[dict], *, policy: str, seeds: list[int],
                        model_sha256: str | None) -> None:
    """Fail closed instead of accepting guarded/truncated or mismatched receipts.

    This validates the records returned by the simulator; it is not an
    independent audit of their provenance or a substitute for CI game replay.
    """
    if len(records) != len(seeds):
        raise ValueError("Incomplete expected evaluation game count")
    for expected_seed, record in zip(seeds, records):
        if not isinstance(record, dict):
            raise ValueError("Non-object game receipt")
        if (record.get("seed") != expected_seed or record.get("policy") != policy
                or record.get("agent_id") != "evaluation"):
            raise ValueError("Seed, model policy or evaluation identity mismatch")
        if (record.get("completed") is not True
                or record.get("truncated_combats") != 0
                or record.get("turn_limit_end") is not False):
            raise ValueError("Incomplete or truncated eight-seat game")
        if (record.get("engine_source_hash") != ENGINE_HASH
                or record.get("engine_version") != "1.1.0"):
            raise ValueError("Evaluation engine contract drift")
        ranks = record.get("placements")
        if (not isinstance(ranks, list) or len(ranks) != 8
                or sorted(ranks) != list(range(1, 9))):
            raise ValueError("Invalid eight-seat placement permutation")
        if type(record.get("decisions")) is not int or record["decisions"] <= 0:
            raise ValueError("Missing positive controlled-seat decision count")
        if record.get("model_sha256") != model_sha256:
            raise ValueError("Mismatched model weight digest or baseline contamination")
        if (record.get("raw_model_only") is False
                or record.get("guard_forced_ends", 0) != 0
                or record.get("safety_fallback_count", 0) != 0
                or record.get("fallback_count", 0) != 0):
            raise ValueError("Guarded or fallback-assisted game cannot count as raw evaluation")


def paired_statistics(candidate: list[dict], baseline: list[dict]) -> dict:
    """Rank difference on matched seeds; conservative range-based uncertainty.

    Positive delta means candidate is WORSE. The Hoeffding interval assumes
    independent held-out seeds and fixed opponent/seat setup; it is deliberately
    conservative and is NOT a model promotion rule.
    """
    if not candidate or len(candidate) != len(baseline):
        raise ValueError("Paired evidence must have two equally sized nonempty arms")
    if any(c["seed"] != b["seed"] for c, b in zip(candidate, baseline)):
        raise ValueError("Paired evidence seeds differ")
    deltas = [c["placements"][0] - b["placements"][0]
              for c, b in zip(candidate, baseline)]
    mean = statistics.mean(deltas)
    width = 14.0 * math.sqrt(math.log(40.0) / (2.0 * len(deltas)))
    return {
        "paired_sample_size": len(deltas),
        "paired_rank_deltas_candidate_minus_baseline": deltas,
        "paired_mean_placement_delta": mean,
        "paired_mean_delta_95pct_hoeffding_bounds": [
            max(-7.0, mean - width), min(7.0, mean + width)],
        "uncertainty_method": "Conservative Hoeffding bound; independent seeds assumed; not a promotion test",
    }


def evaluate(policy: str | int = "baseline", model: Path | int | None = None,
             games: int | None = None, start_seed: int = 24000,
             compare_baseline: bool = False) -> dict:
    if isinstance(policy, int):
        # Compact baseline-only API: evaluate(games, seed). Preserve legacy API.
        games, start_seed, model, policy = policy, (model if isinstance(model, int) else 24000), None, "baseline"
    if games is None:
        games = 3
    if policy not in {"baseline", "model"}:
        raise ValueError("Unknown evaluation policy")
    if not 1 <= games <= 100:
        raise ValueError("games must be 1..100")
    if policy == "model" and (model is None or not model.is_file()):
        raise FileNotFoundError("Model checkpoint required for evaluation")
    if compare_baseline and policy != "model":
        raise ValueError("Paired baseline comparison requires a model")
    expected_seeds = list(range(start_seed, start_seed + games))
    model_sha256 = (hashlib.sha256(model.read_bytes()).hexdigest()
                    if policy == "model" else None)
    candidate = [
        run(seed, "evaluation", policy, str(model) if model else None)
        for seed in expected_seeds
    ]
    validate_real_games(candidate, policy=policy, seeds=expected_seeds,
                        model_sha256=model_sha256)
    report = {
        "policy": policy,
        "model_sha256": model_sha256,
        "engine_version": "1.1.0",
        "engine_source_hash": ENGINE_HASH,
        "controlled_seat": 0,
        "fallback_allowed": False,
        "candidate": summarize(candidate),
        "seed_start": start_seed,
        "comparison": "seven scripted TavernGym bots, not Arena Elo",
        "inference": "Descriptive results only; small samples do not establish improvement",
    }
    if compare_baseline:
        baseline = [run(seed, "evaluation", "baseline") for seed in expected_seeds]
        validate_real_games(baseline, policy="baseline", seeds=expected_seeds,
                            model_sha256=None)
        report["baseline"] = summarize(baseline)
        report.update(paired_statistics(candidate, baseline))
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--policy", choices=["model", "baseline"])
    p.add_argument("--model", type=Path)
    p.add_argument("--compare-baseline", action="store_true")
    p.add_argument("--games", type=int, default=3)
    p.add_argument("--start-seed", type=int, default=24000)
    p.add_argument("--out", type=Path, default=Path("artifacts/evaluation.json"))
    a = p.parse_args()
    policy = a.policy or ("model" if a.model is not None else "baseline")
    report = evaluate(policy, a.model, a.games, a.start_seed, a.compare_baseline)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    main()
