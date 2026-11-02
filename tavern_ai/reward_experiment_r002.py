"""Round 002: longer isolated potential shaping test with 20 paired full games."""
from __future__ import annotations
import argparse
import json
import random
import statistics
from pathlib import Path

from .contract import verify_engine
from .reward_experiment import (
    GAMMA, SESSION_ID, SHAPING_ALPHA, train_arm, run_capped_full_game,
)

EVAL_SEEDS = tuple(range(32001, 32021))


def evaluate(name: str, checkpoint: Path, receipts: Path | None):
    games = []
    for seed in EVAL_SEEDS:
        receipt = run_capped_full_game(seed, checkpoint)
        if receipts is not None:
            receipts.mkdir(parents=True, exist_ok=True)
            (receipts / f"002-{seed}.json").write_text(
                json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
            )
        games.append(receipt)
    ranks = [g["placements"][0] for g in games]
    return {
        "arm": name,
        "games": len(games),
        "seeds": list(EVAL_SEEDS),
        "placements_for_seat_zero": ranks,
        "eight_seat_placements": [g["placements"] for g in games],
        "decisions": [g["decisions"] for g in games],
        "safety_fallback_actions": [g["safety_fallback_actions"] for g in games],
        "invalid_model_actions": sum(g["invalid_model_actions"] for g in games),
        "truncated_combats": sum(g["truncated_combats"] for g in games),
        "turn_limit_ends": sum(g["turn_limit_end"] for g in games),
        "mean_placement": statistics.mean(ranks),
        "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
        "first_place_rate": sum(x == 1 for x in ranks) / len(ranks),
    }


def paired_ci(differences: list[int], bootstraps: int = 2000):
    rng = random.Random(20261102)
    sample_size = len(differences)
    samples = sorted(
        statistics.mean(differences[rng.randrange(sample_size)]
                        for _ in range(sample_size))
        for _ in range(bootstraps)
    )
    return [samples[int(bootstraps * 0.025)],
            samples[min(bootstraps - 1, int(bootstraps * 0.975))]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=22043)
    parser.add_argument("--out", type=Path, default=Path("outputs/reward-r002"))
    args = parser.parse_args()
    if args.steps < 128 or args.steps > 8192 or args.steps % 128:
        parser.error("steps must be multiple of 128 in [128,8192]")
    engine = verify_engine()
    args.out.mkdir(parents=True, exist_ok=True)
    training = {
        key: train_arm(key, alpha, args.steps, args.seed, args.out / f"{key}.zip")
        for key, alpha in (("control", 0.0), ("shaped", SHAPING_ALPHA))
    }
    evaluation = {
        key: evaluate(
            key, args.out / f"{key}.zip",
            Path("experiments") / SESSION_ID if key == "shaped" else None
        )
        for key in ("control", "shaped")
    }
    differences = [
        s - c for s, c in zip(
            evaluation["shaped"]["placements_for_seat_zero"],
            evaluation["control"]["placements_for_seat_zero"]
        )
    ]
    report = {
        "schema": 1, "round": 2, "session_id": SESSION_ID,
        "engine": engine, "gamma": GAMMA, "shaping_alpha": SHAPING_ALPHA,
        "seed": args.seed, "steps_per_arm": args.steps, "evaluation_games_per_arm": 20,
        "training": training, "evaluation": evaluation,
        "shaped_minus_control_rank": differences,
        "mean_rank_difference": statistics.mean(differences),
        "paired_mean_diff_bootstrap_95pct_ci": paired_ci(differences),
        "bootstrap_seed": 20261102, "bootstrap_resamples": 2000,
        "interpretation": "Hold-out paired seeds, action cap disclosed; descriptive not Arena Elo",
        "durability": "Temporary 30-day Actions artifact; no permanent checkpoint.",
    }
    target = Path("research/sessions") / SESSION_ID / "metrics-002.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
