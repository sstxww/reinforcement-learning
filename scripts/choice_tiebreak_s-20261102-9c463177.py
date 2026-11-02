"""Paired real-TavernGym ablation of mandatory choice tie-breaking.

Only behavior change: when two or more actions in [30, 46) are legal,
choose the rightmost instead of the V0 baseline's leftmost.
No simulator patches, fake matches, or PPO promotion claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
from pathlib import Path

import numpy as np

from tavern_ai.baseline import BaselinePolicy
from tavern_ai import canary
from tavern_ai.validate_receipt import validate

SESSION = "s-20261102-9c463177"
DEFAULT_SEEDS = (39001, 39002, 39003, 39004)


class RightmostMandatoryPolicy:
    """Delegate every other decision to the unchanged repository baseline."""

    def __init__(self) -> None:
        self.baseline = BaselinePolicy()
        self.multiple_choice_events = 0
        self.changed_decisions = 0

    def act(self, observation: dict, context: dict | None = None) -> int:
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (245,) or not mask.any():
            raise ValueError("Invalid action mask")
        mandatory = np.flatnonzero(mask[30:46]) + 30
        if len(mandatory) >= 2:
            self.multiple_choice_events += 1
            selected = int(mandatory[-1])
            if selected != self.baseline.act(observation, context):
                self.changed_decisions += 1
            return selected
        return self.baseline.act(observation, context)


def play_candidate(seed: int) -> dict:
    policy = RightmostMandatoryPolicy()
    original = canary.BaselinePolicy
    try:
        canary.BaselinePolicy = lambda: policy
        receipt = canary.run(seed, SESSION, "baseline")
    finally:
        canary.BaselinePolicy = original
    receipt["policy"] = "rightmost-mandatory-baseline"
    receipt["strategy_version"] = "rightmost-mandatory-v1"
    receipt["multiple_choice_events"] = policy.multiple_choice_events
    receipt["changed_decisions"] = policy.changed_decisions
    receipt["strategy_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    validate(receipt)
    return receipt


def play_baseline(seed: int) -> dict:
    receipt = canary.run(seed, SESSION, "baseline")
    receipt["strategy_version"] = "main-baseline-v0"
    validate(receipt)
    return receipt


def summarize(records: list[dict]) -> dict:
    ranks = [int(x["placements"][0]) for x in records]
    return {
        "games": len(ranks),
        "mean_placement": statistics.mean(ranks),
        "first_place_rate": sum(p == 1 for p in ranks) / len(ranks),
        "top4_rate": sum(p <= 4 for p in ranks) / len(ranks),
        "placements": ranks,
        "seeds": [x["seed"] for x in records],
    }


def experiment(seeds: tuple[int, ...], output: Path) -> dict:
    if not seeds or len(seeds) > 8 or len(set(seeds)) != len(seeds):
        raise ValueError("Expected 1..8 distinct evaluation seeds")
    output.mkdir(parents=True, exist_ok=True)
    controls, candidates = [], []
    for idx, seed in enumerate(seeds):
        baseline = play_baseline(seed)
        candidate = play_candidate(seed)
        controls.append(baseline)
        candidates.append(candidate)
        # A unique named mandatory own-session receipt from the first real game.
        candidate_name = f"001-{seed}.json" if idx == 0 else f"candidate-{seed}.json"
        for name, receipt in [(f"baseline-{seed}.json", baseline),
                              (candidate_name, candidate)]:
            path = output / name
            path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "seed": seed,
            "baseline_rank": baseline["placements"][0],
            "candidate_rank": candidate["placements"][0],
            "changed_decisions": candidate["changed_decisions"],
            "candidate_completed": candidate["completed"],
        }), flush=True)
    base_stat = summarize(controls)
    cand_stat = summarize(candidates)
    report = {
        "session_id": SESSION,
        "hypothesis": "Rightmost mandatory choice changes real-game outcomes vs first legal",
        "environment": "real pinned TavernGym engine via tavern_ai.canary.run",
        "engine_version": candidates[0]["engine_version"],
        "engine_source_hash": candidates[0]["engine_source_hash"],
        "source_sha": os.getenv("GITHUB_SHA", ""),
        "run_url": ("https://github.com/sstxww/reinforcement-learning/actions/runs/"
                    + os.getenv("GITHUB_RUN_ID", "unknown")),
        "policy": "rightmost-mandatory-v1 vs unchanged main baseline",
        "actual_training_steps": 0,
        "experiment_type": "pure policy ablation",
        "candidate": cand_stat,
        "baseline": base_stat,
        "paired_rank_deltas": [
            a["placements"][0] - b["placements"][0]
            for a, b in zip(candidates, controls)
        ],
        "paired_mean_placement_delta": cand_stat["mean_placement"] - base_stat["mean_placement"],
        "total_altered_decisions": sum(r["changed_decisions"] for r in candidates),
        "total_multiple_choice_events": sum(r["multiple_choice_events"] for r in candidates),
        "performance_conclusion": "unverified; small paired sample, no significance claim",
        "candidate_model_sha256": None,
        "notes": "Uses exact same seed per paired match; bot RNG can diverge after altered actions.",
    }
    metrics = Path("research/sessions") / SESSION / "round-001-metrics.json"
    metrics.parent.mkdir(parents=True, exist_ok=True)
    metrics.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("FINAL_METRICS=" + json.dumps(report, sort_keys=True), flush=True)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-seed", type=int, default=DEFAULT_SEEDS[0])
    parser.add_argument("--games", type=int, default=4)
    parser.add_argument("--out", type=Path, default=Path("experiments") / SESSION)
    args = parser.parse_args()
    experiment(tuple(range(args.start_seed, args.start_seed + args.games)), args.out)


if __name__ == "__main__":
    main()
