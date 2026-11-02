"""Isolated TavernGym A/B: prefer buying before an otherwise selected tier upgrade.

This is a rule-policy ablation, NOT PPO training. Uses the genuine canary
game driver, pinned TavernGym and seven upstream bots, no fake simulator.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from statistics import mean, stdev

import numpy as np

from . import canary
from .baseline import BaselinePolicy
from .validate_receipt import validate

POLICY = "planned-turn-buy-before-upgrade-v1"
SESSION = "s-20261102-9c034841"
UPGRADE_TURNS = frozenset((2, 5, 7, 9, 11))


class UpgradePriorityPolicy(BaselinePolicy):
    """On planned turns replace a chosen upgrade with a legal purchase."""

    def act(self, observation: dict, context: dict | None = None) -> int:
        context = context or {}
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (245,) or not mask.any():
            raise ValueError("Expected 245-action nonempty mask")
        turn = int(context.get("turn", 0))
        used = int(context.get("actions_used", 0))
        baseline_action = super().act(observation, context)
        # Preserve higher-priority discovery/playing decisions. Only override
        # an upgrade that baseline actually selected, when a buy is legal.
        if baseline_action == 3 and turn in UPGRADE_TURNS and used < 3:
            buy = np.flatnonzero(mask[8:16])
            if buy.size:
                return int(buy[0] + 8)
        return baseline_action


def real_match(seed: int, candidate: bool) -> dict:
    """Run the complete real game with explicit, scoped policy injection.

    canary.run constructs the BaselinePolicy once for seat zero. Temporarily
    replacing that constructor changes only seat zero's decisions; other
    seven seats continue using Game.bot_play. No game rules are modified.
    """
    if not candidate:
        receipt = canary.run(seed, SESSION, "baseline")
        receipt["comparison_arm"] = "original-baseline"
    else:
        original = canary.BaselinePolicy
        try:
            canary.BaselinePolicy = UpgradePriorityPolicy
            receipt = canary.run(seed, SESSION, "baseline")
        finally:
            canary.BaselinePolicy = original
        receipt["policy"] = POLICY
        receipt["comparison_arm"] = "upgrade-first"
    receipt["policy_source"] = "tavern_ai/upgrade_priority_s_20261102_9c034841.py"
    validate(receipt)
    if receipt["completed"] is not True:
        raise RuntimeError("Incomplete simulator match")
    return receipt


def run_experiment(output: Path, seed: int, eval_seeds: list[int]) -> dict:
    if len(set([seed] + eval_seeds)) != len(eval_seeds) + 1:
        raise ValueError("Evaluation and mandatory game seeds must be distinct")
    if not 2 <= len(eval_seeds) <= 12:
        raise ValueError("Expected 2..12 held-out seeds")
    output.mkdir(parents=True, exist_ok=True)
    own = real_match(seed, True)
    own_path = output / f"001-{seed}.json"
    own_path.write_text(json.dumps(own, indent=2), encoding="utf-8")
    print("MANDATORY_RECEIPT=" + json.dumps(own, sort_keys=True), flush=True)

    baseline, candidate = [], []
    for s in eval_seeds:
        b = real_match(s, False)
        c = real_match(s, True)
        baseline.append(b)
        candidate.append(c)
        print("EVAL_BASELINE_RECEIPT=" + json.dumps(b, sort_keys=True), flush=True)
        print("EVAL_CANDIDATE_RECEIPT=" + json.dumps(c, sort_keys=True), flush=True)

    b_places = [r["placements"][0] for r in baseline]
    c_places = [r["placements"][0] for r in candidate]
    deltas = [c - b for c, b in zip(c_places, b_places)]
    report = {
        "session_id": SESSION,
        "branch": os.getenv("GITHUB_REF_NAME", ""),
        "commit": os.getenv("GITHUB_SHA", ""),
        "engine_version": own["engine_version"],
        "engine_source_hash": own["engine_source_hash"],
        "policy": POLICY,
        "training_steps": 0,
        "experiment_type": "rule-policy-tuning, no PPO weights",
        "mandatory_game": own,
        "eval_seeds": eval_seeds,
        "baseline_placements": b_places,
        "candidate_placements": c_places,
        "paired_candidate_minus_baseline": deltas,
        "baseline_mean_placement": mean(b_places),
        "candidate_mean_placement": mean(c_places),
        "paired_mean_delta": mean(deltas),
        "paired_delta_sample_sd": stdev(deltas),
        "baseline_top4_rate": sum(x <= 4 for x in b_places) / len(b_places),
        "candidate_top4_rate": sum(x <= 4 for x in c_places) / len(c_places),
        "baseline_first_rate": sum(x == 1 for x in b_places) / len(b_places),
        "candidate_first_rate": sum(x == 1 for x in c_places) / len(c_places),
        "uncertainty": "Descriptive, small sample; no strength improvement claimed",
        "model_checkpoint": None,
    }
    (output / "paired-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("PAIRED_REPORT=" + json.dumps({k:v for k,v in report.items() if k != "mandatory_game"}, sort_keys=True), flush=True)
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seed", type=int, default=49101)
    p.add_argument("--eval-seeds", type=int, nargs="+", default=[49111, 49112, 49113, 49114])
    args = p.parse_args()
    run_experiment(args.out, args.seed, args.eval_seeds)


if __name__ == "__main__":
    main()
