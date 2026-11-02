"""Round 002: instrument one-vs-three early purchase overrides on REAL TavernGym."""
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

SESSION = "s-20261102-9c034841"
PLANNED_TURNS = frozenset((2, 5, 7, 9, 11))
NAMES = {"once": "planned-buy-first-decision-r002",
         "three": "planned-buy-first-three-decisions-r001-replay",
         "baseline": "baseline"}


class TracedBuyPolicy(BaselinePolicy):
    def __init__(self, max_initial_actions: int):
        if max_initial_actions not in (1, 3):
            raise ValueError("Only the planned one-vs-three arms are supported")
        self.max_initial_actions = max_initial_actions
        self.upgrade_to_buy_overrides = 0

    def act(self, observation: dict, context: dict | None = None) -> int:
        context = context or {}
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (245,) or not mask.any():
            raise ValueError("Expected 245-action nonempty mask")
        choice = super().act(observation, context)
        turn = int(context.get("turn", 0))
        used = int(context.get("actions_used", 0))
        if choice == 3 and turn in PLANNED_TURNS and used < self.max_initial_actions:
            buys = np.flatnonzero(mask[8:16])
            if buys.size:
                self.upgrade_to_buy_overrides += 1
                return int(buys[0] + 8)
        return choice


def real_match(seed: int, arm: str) -> dict:
    if arm not in NAMES:
        raise ValueError("Unknown arm")
    if arm == "baseline":
        r = canary.run(seed, SESSION, "baseline")
        overrides = 0
    else:
        p = TracedBuyPolicy(1 if arm == "once" else 3)
        old = canary.BaselinePolicy
        try:
            # Scoped only to seat-zero policy constructor in canary.run.
            # The real engine and seven official Game.bot_play bots are untouched.
            canary.BaselinePolicy = lambda: p
            r = canary.run(seed, SESSION, "baseline")
        finally:
            canary.BaselinePolicy = old
        overrides = p.upgrade_to_buy_overrides
    r["policy"] = NAMES[arm]
    r["comparison_arm"] = arm
    r["upgrade_to_buy_overrides"] = overrides
    r["policy_source"] = "tavern_ai/upgrade_frequency_s_20261102_9c034841.py"
    validate(r)
    if r["completed"] is not True:
        raise RuntimeError("TavernGym game incomplete")
    return r


def summarize(matches: list[dict]) -> dict:
    ranks = [r["placements"][0] for r in matches]
    decisions = [r["decisions"] for r in matches]
    overrides = [r["upgrade_to_buy_overrides"] for r in matches]
    return {"games": len(matches), "ranks": ranks, "mean_placement": mean(ranks),
            "first_rate": sum(x == 1 for x in ranks) / len(ranks),
            "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
            "decisions": decisions, "mean_decisions": mean(decisions),
            "overrides": overrides, "total_overrides": sum(overrides)}


def run_experiment(output: Path, seed: int, eval_seeds: list[int]) -> dict:
    if not 2 <= len(eval_seeds) <= 8 or len(set([seed] + eval_seeds)) != 1 + len(eval_seeds):
        raise ValueError("Need 2..8 distinct held-out seeds and distinct own seed")
    output.mkdir(parents=True, exist_ok=True)
    own = real_match(seed, "once")
    (output / f"002-{seed}.json").write_text(json.dumps(own, indent=2), encoding="utf-8")
    print("R002_MANDATORY=" + json.dumps(own, sort_keys=True), flush=True)
    groups = {"baseline": [], "three": [], "once": []}
    tags = {"baseline": "R002_BASELINE=", "three": "R002_THREE=", "once": "R002_ONCE="}
    for s in eval_seeds:
        for arm in ("baseline", "three", "once"):
            r = real_match(s, arm)
            groups[arm].append(r)
            print(tags[arm] + json.dumps(r, sort_keys=True), flush=True)
    stats = {arm: summarize(xs) for arm, xs in groups.items()}
    diff = [a - b for a, b in zip(stats["once"]["ranks"], stats["three"]["ranks"])]
    report = {
        "session_id": SESSION,
        "round": 2,
        "commit": os.getenv("GITHUB_SHA", ""),
        "engine_version": own["engine_version"],
        "engine_source_hash": own["engine_source_hash"],
        "training_steps": 0,
        "comparison": "genuine TavernGym games, not Arena; original baseline vs once-vs-three overrides",
        "eval_seeds": eval_seeds,
        "own_game": own,
        "stats": stats,
        "once_minus_three_placement": diff,
        "paired_mean_delta_once_minus_three": mean(diff),
        "paired_sample_sd": stdev(diff),
        "uncertainty": "n=4 descriptive; do not claim a verified gain",
        "model_checkpoint": None,
    }
    (output / "round-002-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    compact = {k:v for k,v in report.items() if k != "own_game"}
    print("R002_SUMMARY=" + json.dumps(compact, sort_keys=True), flush=True)
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=49201)
    p.add_argument("--eval-seeds", type=int, nargs="+", default=[49211, 49212, 49213, 49214])
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    run_experiment(args.out, args.seed, args.eval_seeds)


if __name__ == "__main__":
    main()
