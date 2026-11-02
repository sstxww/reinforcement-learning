"""Held-out confirmatory evaluation of session Round-001's exact same rule policy."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
from pathlib import Path

from .purchase_before_play_s64405d5e import SESSION_ID, record, run_match


def paired_statistics(rows: list[dict], *, bootstrap_seed: int = 20261102, draws: int = 4000) -> dict:
    """Paired placement differences: candidate minus control (negative is better)."""
    if not rows:
        raise ValueError("Cannot summarize zero paired games")
    control = [int(row["baseline_rank"]) for row in rows]
    candidate = [int(row["candidate_rank"]) for row in rows]
    diffs = [c - b for c, b in zip(candidate, control)]
    rng = random.Random(bootstrap_seed)
    boot_means = sorted(
        statistics.mean(rng.choice(diffs) for _ in diffs)
        for _ in range(draws)
    )
    return {
        "pairs": len(rows),
        "baseline_ranks": control,
        "candidate_ranks": candidate,
        "baseline_mean_rank": statistics.mean(control),
        "candidate_mean_rank": statistics.mean(candidate),
        "paired_mean_rank_delta": statistics.mean(diffs),
        "paired_bootstrap_95pct_interval": [
            boot_means[int(0.025 * draws)],
            boot_means[min(draws - 1, int(0.975 * draws))],
        ],
        "baseline_first_rate": sum(x == 1 for x in control) / len(rows),
        "candidate_first_rate": sum(x == 1 for x in candidate) / len(rows),
        "baseline_top4_rate": sum(x <= 4 for x in control) / len(rows),
        "candidate_top4_rate": sum(x <= 4 for x in candidate) / len(rows),
        "candidate_better_games": sum(d < 0 for d in diffs),
        "candidate_worse_games": sum(d > 0 for d in diffs),
        "equal_rank_games": sum(d == 0 for d in diffs),
        "candidate_interventions": sum(int(row["candidate_interventions"]) for row in rows),
        "paired_rows": rows,
        "interval_note": "Exploratory paired percentile bootstrap; not proof of policy generalization.",
    }


def experiment(*, seed: int, paired_seed: int, pairs: int, out_dir: Path, report_path: Path) -> dict:
    if not 2 <= pairs <= 40:
        raise ValueError("Confirmatory pairs must be 2..40")
    if seed >= paired_seed and seed < paired_seed + pairs:
        raise ValueError("Primary candidate seed must not overlap held-out paired seeds")
    main_receipt = run_match(seed, candidate=True)
    record(out_dir / f"002-{seed}.json", main_receipt)
    rows = []
    for i in range(pairs):
        s = paired_seed + i
        control = run_match(s, candidate=False)
        candidate = run_match(s, candidate=True)
        record(out_dir / "controls" / f"002-{s}.json", control)
        record(out_dir / f"002-{s}.json", candidate)
        rows.append({
            "seed": s,
            "baseline_rank": control["placements"][0],
            "candidate_rank": candidate["placements"][0],
            "candidate_interventions": candidate["interventions"],
            "baseline_decisions": control["decisions"],
            "candidate_decisions": candidate["decisions"],
            "candidate_turns": candidate["turns"],
        })
    summary = paired_statistics(rows)
    summary.update({
        "session_id": SESSION_ID,
        "round": 2,
        "hypothesis": "First-round small ranking advantage survives fresh independent seeds",
        "primary_seed": seed,
        "primary_rank": main_receipt["placements"][0],
        "primary_decisions": main_receipt["decisions"],
        "primary_completed": main_receipt["completed"],
        "primary_placements": main_receipt["placements"],
        "engine_version": main_receipt["engine_version"],
        "engine_source_hash": main_receipt["engine_source_hash"],
        "policy_sha256": main_receipt["policy_sha256"],
        "evaluation_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "training_steps": 0,
        "model_sha256": None,
        "interpretation": "Independent confirmation required before any claim of strength gain.",
    })
    record(report_path, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=41100)
    parser.add_argument("--paired-seed", type=int, default=41101)
    parser.add_argument("--pairs", type=int, default=20)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments") / SESSION_ID)
    parser.add_argument("--report", type=Path, default=Path("reports") / SESSION_ID / "paired-002.json")
    args = parser.parse_args()
    experiment(seed=args.seed, paired_seed=args.paired_seed, pairs=args.pairs,
               out_dir=args.out_dir, report_path=args.report)


if __name__ == "__main__":
    main()
