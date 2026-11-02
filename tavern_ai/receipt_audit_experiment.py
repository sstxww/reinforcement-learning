"""Bounded REAL engine three-game evidence audit, plus synthetic negatives.

Games are run through tavern_ai.canary and must reach Game.is_over().
This is an engineering integrity experiment, NOT PPO training or an
improvement in gameplay strength.
"""
from __future__ import annotations

import argparse
import copy
import json
import statistics
from pathlib import Path

from .canary import run
from .receipt_integrity import validate_integrity
from .validate_receipt import validate as legacy_validate


def mutations(authentic: dict) -> dict[str, dict]:
    cases = {}
    def add(label, field, value):
        forged = copy.deepcopy(authentic)
        forged[field] = value
        cases[label] = forged
    add("duplicate_placements", "placements", [1, 1, 3, 4, 5, 6, 7, 8])
    add("incorrect_engine_hash", "engine_source_hash", "0" * 16)
    add("incorrect_engine_version", "engine_version", "9.9.9")
    add("negative_seed", "seed", -9)
    add("unhashed_model_claim", "policy", "model")
    add("unsupported_policy", "policy", "invented")
    return cases


def audit(seed_start: int, games: int, agent_id: str, output_dir: Path, report_path: Path) -> dict:
    if games < 1 or games > 6:
        raise ValueError("Bounded engineering experiment requires 1..6 games")
    if seed_start < 0:
        raise ValueError("Seed must not be negative")
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    receipts = []
    for offset in range(games):
        seed = seed_start + offset
        authentic = run(seed, agent_id, "baseline")
        validate_integrity(authentic)
        receipt_path = output_dir / f"001-{seed}.json"
        receipt_path.write_text(json.dumps(authentic, indent=2), encoding="utf-8")
        receipts.append(authentic)
        results.append({
            "seed": seed, "receipt": str(receipt_path),
            "rank": authentic["placements"][0], "placements": authentic["placements"],
            "decisions": authentic["decisions"], "turns": authentic["turns"],
            "completed": authentic["completed"],
            "truncated_combats": authentic["truncated_combats"],
            "turn_limit_end": authentic["turn_limit_end"],
        })
    acceptance = []
    for name, mutated in mutations(receipts[0]).items():
        old_ok = new_ok = True
        try:
            legacy_validate(mutated)
        except ValueError:
            old_ok = False
        try:
            validate_integrity(mutated)
        except ValueError:
            new_ok = False
        acceptance.append({"case": name, "legacy_accepted": old_ok,
                           "strict_accepted": new_ok})
        if new_ok:
            raise RuntimeError(f"Strict receipt audit failed to reject {name}")
    ranks = [r["rank"] for r in results]
    report = {
        "schema": 1, "agent_id": agent_id, "experiment": "receipt_integrity",
        "policy": "baseline", "ppo_training_steps": 0,
        "games": games, "seeds": [r["seed"] for r in results],
        "mean_placement": statistics.mean(ranks),
        "first_place_rate": sum(r == 1 for r in ranks) / games,
        "top4_rate": sum(r <= 4 for r in ranks) / games,
        "results": results, "negative_mutation_tests": acceptance,
        "legacy_false_acceptances": sum(x["legacy_accepted"] for x in acceptance),
        "strict_false_acceptances": sum(x["strict_accepted"] for x in acceptance),
        "interpretation": "Engineering evidence only; no gameplay-strength claim."
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--agent-id", required=True)
    p.add_argument("--seed-start", type=int, default=36001)
    p.add_argument("--games", type=int, default=3)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    audit(a.seed_start, a.games, a.agent_id, a.out_dir, a.report)


if __name__ == "__main__":
    main()
