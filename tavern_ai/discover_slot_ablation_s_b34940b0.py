"""Isolated, real-TavernGym paired discover-slot experiment for s-20261102-b34940b0.

The sole intervention is to choose the last, rather than the first, legal
forced choice in the reserved action band [30, 46). All other decisions use
the unchanged mainline BaselinePolicy. No PPO weights are trained here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
from pathlib import Path

import numpy as np

from . import canary
from .baseline import BaselinePolicy
from .validate_receipt import validate

SESSION_ID = "s-20261102-b34940b0"
POLICY_VERSION = "discover-last-v1"


class LastDiscoverPolicy(BaselinePolicy):
    forced_choices = 0
    multi_option_choices = 0

    def act(self, observation: dict, context: dict | None = None) -> int:
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (245,) or not mask.any():
            raise ValueError("Expected 245-action nonempty mask")
        legal = np.flatnonzero(mask[30:46])
        if legal.size:
            type(self).forced_choices += 1
            if legal.size > 1:
                type(self).multi_option_choices += 1
            return int(30 + legal[-1])
        return super().act(observation, context)


def play(seed: int, policy: str) -> dict:
    if policy not in {"baseline", POLICY_VERSION}:
        raise ValueError(f"Unknown policy: {policy}")
    original_class = canary.BaselinePolicy
    LastDiscoverPolicy.forced_choices = 0
    LastDiscoverPolicy.multi_option_choices = 0
    try:
        # Scope the intervention to this invocation; the simulator and
        # canary's Game.is_over() safety/receipt logic remain unchanged.
        if policy == POLICY_VERSION:
            canary.BaselinePolicy = LastDiscoverPolicy
        receipt = canary.run(seed, SESSION_ID, "baseline")
    finally:
        canary.BaselinePolicy = original_class
    receipt["policy"] = policy
    receipt["policy_version"] = POLICY_VERSION if policy != "baseline" else "main-baseline"
    receipt["multi_option_discover_choices"] = (
        LastDiscoverPolicy.multi_option_choices if policy != "baseline" else None
    )
    receipt["forced_discover_choices"] = (
        LastDiscoverPolicy.forced_choices if policy != "baseline" else None
    )
    receipt["policy_source_sha256"] = hashlib.sha256(
        Path(__file__).read_bytes()
        if policy != "baseline"
        else Path(original_class.__module__.replace(".", "/") + ".py").read_bytes()
    ).hexdigest()
    validate(receipt)
    return receipt


def summary(receipts: list[dict]) -> dict:
    placements = [int(r["placements"][0]) for r in receipts]
    n = len(placements)
    return {
        "games": n,
        "seeds": [r["seed"] for r in receipts],
        "placements": placements,
        "mean_placement": statistics.mean(placements),
        "first_place_rate": sum(x == 1 for x in placements) / n,
        "top4_rate": sum(x <= 4 for x in placements) / n,
        "completed": all(r["completed"] for r in receipts),
        "illegal_actions": 0,  # canary rejects any illegal action
        "truncated_combats": sum(r["truncated_combats"] for r in receipts),
    }


def experiment(start_seed: int, games: int, out_dir: Path, report: Path) -> dict:
    if not 1 <= games <= 12:
        raise ValueError("games must be 1..12")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "controls").mkdir(parents=True, exist_ok=True)
    baseline, candidate = [], []
    for seed in range(start_seed, start_seed + games):
        control = play(seed, "baseline")
        control_path = out_dir / "controls" / f"001-{seed}.json"
        control_path.write_text(json.dumps(control, indent=2) + "\n", encoding="utf-8")
        baseline.append(control)
        print(f"baseline complete seed={seed} rank={control['placements'][0]}", flush=True)

        alternate = play(seed, POLICY_VERSION)
        candidate_path = out_dir / f"001-{seed}.json"
        candidate_path.write_text(json.dumps(alternate, indent=2) + "\n", encoding="utf-8")
        candidate.append(alternate)
        print(
            f"candidate complete seed={seed} rank={alternate['placements'][0]}"
            f" multi_option_choices={alternate['multi_option_discover_choices']}",
            flush=True,
        )
    report_data = {
        "session_id": SESSION_ID,
        "hypothesis": "Selecting the last legal compulsory discovery choice may improve rank",
        "baseline_commit": "315b068bac5ab6d8403c3c9b18f8c101c0cded5d",
        "environment": "real pinned TavernGym / 7 official bots",
        "game_engine_source_hash": candidate[0]["engine_source_hash"],
        "game_engine_version": candidate[0]["engine_version"],
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "github_sha": os.getenv("GITHUB_SHA"),
        "learning_steps": 0,
        "training_type": "rule-policy ablation (no neural training)",
        "control": summary(baseline),
        "candidate": summary(candidate),
        "paired_candidate_minus_control": [
            b["placements"][0] - a["placements"][0]
            for a, b in zip(baseline, candidate)
        ],
        "mean_rank_delta": (
            summary(candidate)["mean_placement"] - summary(baseline)["mean_placement"]
        ),
        "multi_option_discover_choices": sum(
            r["multi_option_discover_choices"] for r in candidate
        ),
        "conclusion": "Exploratory only; no statistical strength claim",
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(report_data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report_data), flush=True)
    return report_data


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=65201)
    p.add_argument("--games", type=int, default=4)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    experiment(a.seed, a.games, a.output_dir, a.report)


if __name__ == "__main__":
    main()
