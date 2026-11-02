"""Paired held-out authentic eight-seat guarded-model evaluation after PPO resume.

This is an exploratory low-n paired diagnostic; it never promotes Champion.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from .checkpoint_registry import file_sha256
from .rank8_probe_decfc670 import trace
from .validate_receipt import validate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--training-report", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    evidence = json.loads(args.training_report.read_text(encoding="utf-8"))
    before_hash, after_hash = file_sha256(args.before), file_sha256(args.after)
    if before_hash != evidence["source_model_sha256"] or after_hash != evidence["new_model_sha256"]:
        raise ValueError("Evaluation checkpoint differs from verified resumed checkpoint")
    if evidence["new_total_timesteps"] != evidence["old_total_timesteps"] + 128:
        raise ValueError("Evaluation requires an actual 128-step continuation")
    from sb3_contrib import MaskablePPO
    models = {
        "old": (MaskablePPO.load(str(args.before), device="cpu"), before_hash),
        "resumed": (MaskablePPO.load(str(args.after), device="cpu"), after_hash),
    }
    seeds = [86271, 86272]
    records = {label: [] for label in models}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for label, (model, sha) in models.items():
        for seed in seeds:
            receipt = trace(seed, model, sha)
            validate(receipt)
            receipt["arm"] = label
            target = args.out_dir / f"003-{label}-{seed}.json"
            target.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            records[label].append(receipt)
            print(json.dumps({"arm": label, "seed": seed, "rank": receipt["placements"][0],
                              "buys": receipt["actual_buys"],
                              "forced_ends": receipt["guard_forced_end_turns"]}), flush=True)
    def summary(label: str):
        rows = records[label]
        ranks = [r["placements"][0] for r in rows]
        return {
            "placements": ranks,
            "mean_placement": statistics.mean(ranks),
            "top4_rate": sum(r <= 4 for r in ranks) / len(ranks),
            "win_rate": sum(r == 1 for r in ranks) / len(ranks),
            "actual_buys": sum(r["actual_buys"] for r in rows),
            "legal_buy_opportunities": sum(r["legal_buy_opportunity_decisions"] for r in rows),
            "model_end_when_buy_legal": sum(r["model_ends_with_legal_buy"] for r in rows),
            "guard_forced_ends": sum(r["guard_forced_end_turns"] for r in rows),
            "total_actions": sum(r["decisions"] for r in rows),
        }
    old, new = summary("old"), summary("resumed")
    report = {
        "schema": 1, "kind": "paired_guarded_real_full_game_heldout",
        "seeds": seeds, "n_pairs": len(seeds),
        "old_model_sha256": before_hash, "resumed_model_sha256": after_hash,
        "old": old, "resumed": new,
        "paired_rank_delta_resumed_minus_old": [
            b["placements"][0] - a["placements"][0]
            for a, b in zip(records["old"], records["resumed"])
        ],
        "paired_mean_rank_delta": new["mean_placement"] - old["mean_placement"],
        "proven_competitive_improvement": False,
        "champion_promoted": False,
        "interpretation": "Exploratory, only two paired full games with guard interventions tracked separately. No Arena MMR, no promotion.",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
