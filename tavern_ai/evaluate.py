"""Seeded full-game evaluation, with optional paired baseline comparison."""
from __future__ import annotations
import argparse, json, statistics
from pathlib import Path
from .canary import run
from .receipt_integrity import validate_integrity

def summarize(records: list[dict]) -> dict:
    if not records:
        raise ValueError("Cannot summarize zero games")
    placements = [r["placements"][0] for r in records]
    return {
        "games": len(records),
        "mean_placement": statistics.mean(placements),
        "top4_rate": sum(x <= 4 for x in placements) / len(records),
        "first_place_rate": sum(x == 1 for x in placements) / len(records),
        "placements": placements, "seeds": [r["seed"] for r in records],
    }

def _verify_full_game_records(records: list[dict], policy: str, seeds: list[int]) -> None:
    """Fail closed on malformed, mismatched or duplicate full-game evidence.

    Only the raw tavern_ai.canary runner is used for policy evaluation. A
    rescued / fallback-policy game is not interchangeable with that runner.
    """
    if len(records) != len(seeds):
        raise ValueError("Missing or duplicate evaluation game receipts")
    seen: set[int] = set()
    model_hashes: set[str] = set()
    for record, expected_seed in zip(records, seeds):
        validate_integrity(record)
        actual_seed = record["seed"]
        if actual_seed != expected_seed or actual_seed in seen:
            raise ValueError("Evaluation receipt seed mismatch or duplicate")
        if record["policy"] != policy:
            raise ValueError("Evaluation receipt policy mismatch")
        if record.get("seat", 0) != 0:
            raise ValueError("This evaluation runner controls seat zero only")
        if record.get("fallback_actions", 0) != 0 or record.get("guard_forced_ends", 0) != 0:
            raise ValueError("Guarded or fallback receipts require a separate evaluation protocol")
        seen.add(actual_seed)
        if policy == "model":
            model_hashes.add(record["model_sha256"])
    if policy == "model" and len(model_hashes) != 1:
        raise ValueError("Multiple model weight hashes in one evaluation batch")


def evaluate(policy: str | int = "baseline", model: Path | int | None = None, games: int | None = None, start_seed: int = 24000,
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
    candidate = [
        run(start_seed + i, "evaluation", policy, str(model) if model else None)
        for i in range(games)
    ]
    expected_seeds = list(range(start_seed, start_seed + games))
    _verify_full_game_records(candidate, policy, expected_seeds)
    report = {
        "policy": policy, "candidate": summarize(candidate),
        "seed_start": start_seed,
        "comparison": "seven scripted TavernGym bots, not Arena Elo",
        "inference": "Descriptive results only; small samples do not establish improvement",
        "receipt_integrity": "strict eight-seat source/seed/policy/weight verification",
        "controlled_seat": 0,
        "model_evidence_mode": "raw model; guard and fallback not permitted",
    }
    if compare_baseline:
        baseline = [run(start_seed + i, "evaluation", "baseline") for i in range(games)]
        _verify_full_game_records(baseline, "baseline", expected_seeds)
        report["baseline"] = summarize(baseline)
        report["paired_mean_placement_delta"] = (
            report["candidate"]["mean_placement"] - report["baseline"]["mean_placement"]
        )
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
