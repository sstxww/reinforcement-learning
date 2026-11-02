"""Seeded full-game evaluation, with optional paired baseline comparison."""
from __future__ import annotations
import argparse, json, statistics
from pathlib import Path
from .canary import run

def summarize(records: list[dict]) -> dict:
    placements = [r["placements"][0] for r in records]
    return {
        "games": len(records),
        "mean_placement": statistics.mean(placements),
        "top4_rate": sum(x <= 4 for x in placements) / len(records),
        "first_place_rate": sum(x == 1 for x in placements) / len(records),
        "placements": placements, "seeds": [r["seed"] for r in records],
    }

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
    report = {
        "policy": policy, "candidate": summarize(candidate),
        "seed_start": start_seed,
        "comparison": "seven scripted TavernGym bots, not Arena Elo",
        "inference": "Descriptive results only; small samples do not establish improvement",
    }
    if compare_baseline:
        baseline = [run(start_seed + i, "evaluation", "baseline") for i in range(games)]
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
