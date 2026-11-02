"""Session-scoped, deterministic small-sample uncertainty audit for TavernGym games.

Descriptive intervals are *not* an automatic model promotion decision.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
from pathlib import Path
from statistics import mean


def wilson_interval(successes: int, games: int, z: float = 1.959963984540054) -> list[float]:
    """Two-sided Wilson score interval; avoids falsely precise 0%/100% rates."""
    if not isinstance(games, int) or games < 1 or not isinstance(successes, int) or not 0 <= successes <= games:
        raise ValueError("Expected 0 <= successes <= games, with games >= 1")
    if not math.isfinite(z) or z <= 0:
        raise ValueError("z must be positive and finite")
    p = successes / games
    d = 1 + z * z / games
    center = (p + z * z / (2 * games)) / d
    radius = z * math.sqrt(p * (1 - p) / games + z * z / (4 * games * games)) / d
    return [max(0.0, center - radius), min(1.0, center + radius)]


def bootstrap_mean_interval(values: list[float], *, seed: int = 20261102, draws: int = 4000) -> list[float]:
    """Seeded percentile bootstrap over *games*, never individual action decisions."""
    if not values or draws < 100 or any(not math.isfinite(v) for v in values):
        raise ValueError("Expected nonempty finite game values and >=100 draws")
    rng = random.Random(seed)
    n = len(values)
    estimates = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(draws))
    return [estimates[int(0.025 * (draws - 1))], estimates[int(0.975 * (draws - 1))]]


def _seeds_and_ranks(records: list[dict]) -> dict[int, int]:
    if not records:
        raise ValueError("At least one completed game required")
    out = {}
    for r in records:
        if r.get("completed") is not True or r.get("environment") != "TavernGym":
            raise ValueError("Non-TavernGym or incomplete receipt")
        seed, placements = r.get("seed"), r.get("placements")
        if type(seed) is not int or type(placements) is not list or len(placements) != 8:
            raise ValueError("Invalid seed or eight-seat placements")
        if sorted(placements) != list(range(1, 9)) or any(type(v) is not int for v in placements):
            raise ValueError("Placements must be a permutation of ranks 1..8")
        if seed in out:
            raise ValueError("Duplicate seed would overstate independent game count")
        out[seed] = placements[0]
    return out


def solo_summary(records: list[dict], *, bootstrap_seed: int = 20261102) -> dict:
    rank_by_seed = _seeds_and_ranks(records)
    seeds = sorted(rank_by_seed)
    ranks = [rank_by_seed[s] for s in seeds]
    n = len(ranks)
    wins, top4 = sum(v == 1 for v in ranks), sum(v <= 4 for v in ranks)
    return {
        "games": n, "seeds": seeds, "ranks": ranks,
        "mean_rank": mean(ranks),
        "mean_rank_bootstrap_95pct": bootstrap_mean_interval(ranks, seed=bootstrap_seed),
        "first_place_rate": wins / n, "first_place_wilson_95pct": wilson_interval(wins, n),
        "top4_rate": top4 / n, "top4_wilson_95pct": wilson_interval(top4, n),
        "insufficient_for_strength_claim": n < 30,
        "interpretation": "Descriptive 95% intervals, not proof of strength; multiple seeds and sufficient training required.",
    }


def paired_summary(candidate: list[dict], control: list[dict], *, bootstrap_seed: int = 20261102) -> dict:
    """Bootstrap per-seed paired rank differences (candidate minus control)."""
    c, b = _seeds_and_ranks(candidate), _seeds_and_ranks(control)
    if set(c) != set(b):
        raise ValueError("Paired comparison requires exactly identical seed sets")
    seeds = sorted(c)
    deltas = [c[s] - b[s] for s in seeds]
    return {
        "games_per_arm": len(seeds), "seeds": seeds, "paired_rank_deltas": deltas,
        "candidate_minus_control_mean_rank": mean(deltas),
        "paired_bootstrap_95pct": bootstrap_mean_interval(deltas, seed=bootstrap_seed),
        "insufficient_for_strength_claim": len(seeds) < 30,
        "interpretation": "Rank lower is better; CI crossing zero does not establish a gain.",
    }


def run_experiment(agent_id: str, seed_start: int, games: int, receipt_dir: Path, metrics: Path) -> dict:
    if games < 1 or games > 12:
        raise ValueError("Experiment budget must be 1..12 complete games")
    from .canary import run
    from .validate_receipt import validate
    receipts = []
    for i in range(games):
        seed = seed_start + i
        row = run(seed, agent_id, policy="baseline")
        validate(row)
        path = receipt_dir / f"001-{seed}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        receipts.append(row)
    result = {
        "session_id": agent_id, "experiment": "baseline rank uncertainty (not a PPO experiment)",
        "policy": "baseline", "actual_ppo_train_steps": 0,
        "github_run_url": "https://github.com/" + os.environ.get("GITHUB_REPOSITORY", "sstxww/reinforcement-learning") + "/actions/runs/" + os.environ.get("GITHUB_RUN_ID", "unknown"),
        "git_sha_at_run_start": os.environ.get("GITHUB_SHA", ""),
        "engine_version": receipts[0]["engine_version"],
        "engine_source_hash": receipts[0]["engine_source_hash"],
        "total_decisions": sum(r["decisions"] for r in receipts),
        "truncated_combats": sum(r["truncated_combats"] for r in receipts),
        "turn_limit_end": any(r["turn_limit_end"] for r in receipts),
        "all_completed": all(r["completed"] for r in receipts),
        "statistics": solo_summary(receipts),
        "model_checkpoint": None,
        "claim": "Baseline-only variability diagnostic; no policy or PPO improvement claimed.",
    }
    metrics.parent.mkdir(parents=True, exist_ok=True)
    metrics.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--agent-id", required=True)
    p.add_argument("--seed-start", type=int, default=392500)
    p.add_argument("--games", type=int, default=4)
    p.add_argument("--receipt-dir", type=Path, required=True)
    p.add_argument("--metrics", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(run_experiment(args.agent_id, args.seed_start, args.games, args.receipt_dir, args.metrics), ensure_ascii=False))


if __name__ == "__main__":
    main()
