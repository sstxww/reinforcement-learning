"""Strict paired evidence for the latest unpromoted TavernGym Release.

Uses the already-integrated public-observation real_trace. Never changes
model actions, applies a fallback, promotes a Champion or enters Arena.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def summarize_pairs(pairs: list[dict], model_id: str, model_sha256: str) -> dict:
    if not pairs:
        raise ValueError("No paired authentic full-game observations")
    observed_seeds: set[int] = set()
    reports: dict[str, dict] = {}
    for policy in ("baseline", "model"):
        records = []
        for pair in pairs:
            seed = pair.get("seed")
            if type(seed) is not int or seed < 0:
                raise ValueError("Invalid seed")
            receipt = pair.get(policy)
            if not isinstance(receipt, dict) or receipt.get("completed") is not True:
                raise ValueError("Missing authentic completed game")
            if receipt.get("seed") != seed or receipt.get("policy") != policy:
                raise ValueError("Mismatched paired seed/policy")
            if policy == "model" and receipt.get("model_sha256") != model_sha256:
                raise ValueError("Candidate model SHA changed across evaluation")
            if policy == "baseline" and receipt.get("model_sha256") is not None:
                raise ValueError("Baseline must not load model weights")
            if receipt.get("model_guard_forced_end") != 0:
                raise ValueError("Guarded/fallback games are not raw-model evidence")
            placements = receipt.get("placements")
            if not isinstance(placements, list) or len(placements) != 8 or sorted(placements) != list(range(1, 9)):
                raise ValueError("Not an eight-seat complete-game placement permutation")
            opportunity = receipt.get("opportunity_summary")
            if not isinstance(opportunity, dict):
                raise ValueError("Missing legal BUY opportunity telemetry")
            for key in ("buy_legal_decisions", "buy_chosen", "end_while_buy_legal", "decisions"):
                if type(opportunity.get(key)) is not int or opportunity[key] < 0:
                    raise ValueError("Invalid opportunity count")
            if opportunity["buy_chosen"] > opportunity["buy_legal_decisions"]:
                raise ValueError("BUY count exceeds legal BUY chances")
            if opportunity["end_while_buy_legal"] > opportunity["buy_legal_decisions"]:
                raise ValueError("Missed BUY count exceeds legal chances")
            records.append(receipt)
        total_legal = sum(r["opportunity_summary"]["buy_legal_decisions"] for r in records)
        buys = sum(r["opportunity_summary"]["buy_chosen"] for r in records)
        ends = sum(r["opportunity_summary"]["end_while_buy_legal"] for r in records)
        reports[policy] = {
            "ranks": [r["placements"][0] for r in records],
            "mean_rank": statistics.mean(r["placements"][0] for r in records),
            "top4_rate": sum(r["placements"][0] <= 4 for r in records) / len(records),
            "first_place_rate": sum(r["placements"][0] == 1 for r in records) / len(records),
            "actions": sum(r["opportunity_summary"]["decisions"] for r in records),
            "legal_buy_decisions": total_legal, "buy_actions": buys,
            "end_while_buy_legal": ends,
            "buy_given_legal": buys / total_legal if total_legal else None,
            "end_given_legal_buy": ends / total_legal if total_legal else None,
        }
    for pair in pairs:
        if pair["seed"] in observed_seeds:
            raise ValueError("Repeated random seed is not independent evidence")
        observed_seeds.add(pair["seed"])
    return {
        "schema": 1,
        "source": "strict, raw, unguarded full eight-seat TavernGym real_trace",
        "model_id": model_id, "model_sha256": model_sha256,
        "n_paired_games": len(pairs),
        "seeds": [p["seed"] for p in pairs],
        "seat": 0, "seat_rotation": False,
        "baseline": reports["baseline"], "candidate": reports["model"],
        "paired_rank_delta_candidate_minus_baseline": statistics.mean(
            p["model"]["placements"][0] - p["baseline"]["placements"][0] for p in pairs
        ),
        "promoted": False,
        "limitations": "Small n, fixed seat zero and correlated within-match decisions; not proof of competitive gain. A legal BUY is not necessarily a strategically correct BUY.",
    }


def run_evidence(model: Path, metadata: Path, model_id: str, registry: Path,
                 seeds: list[int], out_dir: Path) -> dict:
    from .model_registry import verify_local
    from .registry_integrity import validate_registry
    from .buy_opportunity_68099929 import real_trace

    data = json.loads(registry.read_text(encoding="utf-8"))
    validate_registry(data)
    entry = next((r for r in data["candidates"] if r["id"] == model_id), None)
    if entry is None or data["latest"]["id"] != model_id:
        raise ValueError("Run only on the registered latest unpromoted model")
    gate = verify_local(
        {"id": model_id, "sha256": entry["checkpoint_sha256"],
         "reported_total_timesteps": entry["training_steps"]},
        model, metadata, load=True,
    )
    if not gate["cpu_load_verified"] or not gate["optimizer_state_present"]:
        raise RuntimeError("Candidate load/optimizer preflight failed")
    if len(seeds) != len(set(seeds)) or not 1 <= len(seeds) <= 8:
        raise ValueError("Require 1-8 distinct heldout seeds")
    out_dir.mkdir(parents=True, exist_ok=True)
    pairs = []
    for seed in seeds:
        pair = {"seed": seed}
        for policy in ("baseline", "model"):
            # Raw candidate and baseline play independently. No rescue/fallback.
            receipt = real_trace(seed, f"s-20261102-b71c7aed-{policy}", policy,
                                 model if policy == "model" else None)
            pair[policy] = receipt
            (out_dir / f"raw-{policy}-{seed}.json").write_text(
                json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        pairs.append(pair)
    summary = summarize_pairs(pairs, model_id, gate["sha256"])
    summary["checkpoint_preflight"] = gate
    (out_dir / "paired-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--model-id", required=True)
    p.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    p.add_argument("--seeds", default="920011,920012")
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    report = run_evidence(a.model, a.metadata, a.model_id, a.registry,
                          [int(s) for s in a.seeds.split(",")], a.out_dir)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
