"""Fresh-seed extension of unchanged R002 pre-purchase refresh policy."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

import numpy as np

from .canary import run as baseline_game
from .prebuy_refresh import SESSION_ID, POLICY_VERSION, candidate_game, summary
from .validate_receipt import validate

EXPECTED_SOURCE_SHA256 = "8af4b69abc82f6c7edc415352f23a73a7a502725cdaa1bbd7129b8b2527fd010"


def execute(mandatory_seed: int, start_seed: int, games: int,
            out_dir: Path, report_path: Path) -> dict:
    if not 8 <= games <= 24:
        raise ValueError("R003 extension requires 8..24 real paired games")
    if start_seed <= mandatory_seed < start_seed + games:
        raise ValueError("Canary seed must differ from evaluation seeds")
    actual_hash = hashlib.sha256(
        (Path(__file__).parent / "prebuy_refresh.py").read_bytes()
    ).hexdigest()
    if actual_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("Candidate policy differs from independently evaluated R002 source")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    required = candidate_game(mandatory_seed)
    validate(required)
    (out_dir / f"003-{mandatory_seed}.json").write_text(
        json.dumps(required, indent=2), encoding="utf-8")

    baseline, candidate = [], []
    for s in range(start_seed, start_seed + games):
        b = baseline_game(s, SESSION_ID, "baseline")
        c = candidate_game(s)
        validate(b)
        validate(c)
        baseline.append(b)
        candidate.append(c)
        (out_dir / f"r003-baseline-{s}.json").write_text(
            json.dumps(b, indent=2), encoding="utf-8")
        (out_dir / f"r003-candidate-{s}.json").write_text(
            json.dumps(c, indent=2), encoding="utf-8")

    b, c = summary(baseline), summary(candidate)
    deltas = [new["placements"][0] - old["placements"][0]
              for old, new in zip(baseline, candidate)]
    rng = np.random.default_rng(20261102)
    indices = rng.integers(0, games, size=(10000, games))
    boot_means = np.asarray(deltas, dtype=np.float64)[indices].mean(axis=1)
    ci = np.quantile(boot_means, [0.025, 0.975]).tolist()

    refreshes = [required["refreshes_chosen"]] + [
        row["refreshes_chosen"] for row in candidate
    ]
    result = {
        "session": SESSION_ID,
        "round": 3,
        "hypothesis": "R002 apparent mean-rank gain generalizes to 16 new paired seeds",
        "base_main_sha": "315b068bac5ab6d8403c3c9b18f8c101c0cded5d",
        "engine": {
            "version": required["engine_version"],
            "source_hash": required["engine_source_hash"],
        },
        "policy_version": POLICY_VERSION,
        "policy_sha256": actual_hash,
        "frozen_policy_identical_to_R002": True,
        "ppo_training_steps": 0,
        "model_checkpoint": None,
        "mandatory": {
            "seed": mandatory_seed,
            "rank": required["placements"][0],
            "decisions": required["decisions"],
            "turns": required["turns"],
            "completed": required["completed"],
            "refreshes": required["refreshes_chosen"],
            "receipt": f"experiments/{SESSION_ID}/003-{mandatory_seed}.json",
        },
        "baseline": b,
        "candidate": c,
        "paired_candidate_minus_baseline": deltas,
        "paired_mean_rank_delta": sum(deltas) / games,
        "paired_difference_sample_sd": statistics.stdev(deltas),
        "paired_bootstrap_95pct_CI": ci,
        "bootstrap_resamples": 10000,
        "bootstrap_seed": 20261102,
        "refreshes_per_candidate_game": refreshes,
        "total_refreshes": sum(refreshes),
        "intervention_valid": sum(refreshes) > 0,
        "conclusion": "Descriptive independent extension; evaluate variability before promotion",
    }
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if not result["intervention_valid"]:
        raise RuntimeError("Frozen policy had zero refresh interventions")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mandatory-seed", type=int, default=36520)
    parser.add_argument("--start-seed", type=int, default=36521)
    parser.add_argument("--games", type=int, default=16)
    parser.add_argument("--out-dir", type=Path, default=Path(f"experiments/{SESSION_ID}"))
    parser.add_argument("--report", type=Path, default=Path(f"reports/{SESSION_ID}/round-003.json"))
    args = parser.parse_args()
    execute(args.mandatory_seed, args.start_seed, args.games, args.out_dir, args.report)


if __name__ == "__main__":
    main()
