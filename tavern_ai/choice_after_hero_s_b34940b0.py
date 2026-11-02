"""Real-engine three-arm ablation: is opening hero selection responsible for global last-slot losses?

Only legal `Choose` actions 30..45 are changed. Turn zero is the actual
HeroSelect phase in pinned TavernGym; the posthero arm preserves the
baseline's opening choice and uses the last legal choice from turn 1 onward.
No neural PPO, synthetic simulator, or shared baseline mutation.
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
RULES = ("baseline", "full-last", "posthero-last")


class FullLastPolicy(BaselinePolicy):
    multi_choices = 0

    def act(self, observation, context=None):
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (245,) or not mask.any():
            raise ValueError("Expected 245-action nonempty mask")
        options = np.flatnonzero(mask[30:46])
        if options.size:
            if options.size > 1:
                type(self).multi_choices += 1
            return int(30 + options[-1])
        return super().act(observation, context)


class PostHeroLastPolicy(FullLastPolicy):
    multi_choices = 0

    def act(self, observation, context=None):
        # TavernGym Game::new starts HeroSelect with turn=0. Preserve all
        # first-turn actions. This is not an exact discovery-only filter.
        if int((context or {}).get("turn", 0)) == 0:
            return BaselinePolicy.act(self, observation, context)
        return super().act(observation, context)


def play(seed: int, rule: str) -> dict:
    if rule not in RULES:
        raise ValueError("Unknown rule")
    policy_class = {"baseline": BaselinePolicy, "full-last": FullLastPolicy,
                    "posthero-last": PostHeroLastPolicy}[rule]
    policy_class.multi_choices = 0
    old = canary.BaselinePolicy
    try:
        canary.BaselinePolicy = policy_class
        result = canary.run(seed, SESSION_ID, "baseline")
    finally:
        canary.BaselinePolicy = old
    result["policy"] = rule
    result["policy_version"] = "choice-after-hero-002"
    result["multi_option_choices"] = int(policy_class.multi_choices) if rule != "baseline" else None
    result["policy_sha256"] = hashlib.sha256(
        (Path(__file__) if rule != "baseline" else
         Path(old.__module__.replace(".", "/") + ".py")).read_bytes()
    ).hexdigest()
    validate(result)
    return result


def summarize(records: list[dict]) -> dict:
    ranks = [r["placements"][0] for r in records]
    return {"games": len(ranks), "ranks": ranks,
            "mean_rank": statistics.mean(ranks),
            "top4_rate": sum(r <= 4 for r in ranks) / len(ranks),
            "first_rate": sum(r == 1 for r in ranks) / len(ranks),
            "seeds": [r["seed"] for r in records],
            "completed": all(r["completed"] for r in records),
            "truncated_combats": sum(r["truncated_combats"] for r in records)}


def experiment(seeds: list[int], root: Path, report_path: Path) -> dict:
    if not 1 <= len(seeds) <= 12 or len(set(seeds)) != len(seeds):
        raise ValueError("Require 1..12 distinct seeds")
    records = {r: [] for r in RULES}
    for rule in RULES:
        directory = root if rule == "posthero-last" else root / rule
        directory.mkdir(parents=True, exist_ok=True)
        for seed in seeds:
            receipt = play(seed, rule)
            records[rule].append(receipt)
            p = directory / f"002-{seed}.json"
            p.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            print(f"rule={rule} seed={seed} rank={receipt['placements'][0]}"
                  f" actions={receipt['decisions']} choices={receipt['multi_option_choices']}",
                  flush=True)
    def delta(a: str, b: str) -> list[int]:
        return [int(x["placements"][0] - y["placements"][0])
                for x, y in zip(records[a], records[b])]
    s = {rule: summarize(v) for rule, v in records.items()}
    result = {
        "session_id": SESSION_ID, "round": 2,
        "base_main_sha": "315b068bac5ab6d8403c3c9b18f8c101c0cded5d",
        "run_id": os.getenv("GITHUB_RUN_ID"), "git_sha": os.getenv("GITHUB_SHA"),
        "engine_version": records["baseline"][0]["engine_version"],
        "engine_source_hash": records["baseline"][0]["engine_source_hash"],
        "actual_ppo_steps": 0, "type": "isolated deterministic rule ablation",
        "control": s["baseline"],
        "global_last": s["full-last"],
        "posthero_last": s["posthero-last"],
        "posthero_minus_global_rank_deltas": delta("posthero-last", "full-last"),
        "posthero_minus_baseline_rank_deltas": delta("posthero-last", "baseline"),
        "global_minus_baseline_rank_deltas": delta("full-last", "baseline"),
        "posthero_generic_multi_choices": sum(
            r["multi_option_choices"] for r in records["posthero-last"]),
        "global_generic_multi_choices": sum(
            r["multi_option_choices"] for r in records["full-last"]),
        "interpretation": "Generic Choose 30..45 still includes Discover/target/trinket; "
                          "turn 0 preserves HeroSelect, not a discovery-only experiment. "
                          "Small matched-sample descriptive statistics only.",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seeds", nargs="+", type=int, required=True)
    p.add_argument("--receipts", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    experiment(a.seeds, a.receipts, a.report)


if __name__ == "__main__":
    main()
