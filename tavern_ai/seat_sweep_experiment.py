"""Round 002: real TavernGym eight-seat sensitivity sweep over held-out seeds.

Depends on the independently tested Round-001 real-engine runner, and runs
new complete matches rather than extrapolating the previous results.
"""
from __future__ import annotations
import argparse
import json
import statistics
from pathlib import Path

from .seat_position_experiment import play, verify_controlled_receipt


def summarize_seat(records: list[dict]) -> dict:
    if not records:
        raise ValueError("Cannot summarize empty real-game records")
    for record in records:
        verify_controlled_receipt(record)
    seats = {r["controlled_seat"] for r in records}
    if len(seats) != 1:
        raise ValueError("Each summary must use one controlled seat")
    ranks = [r["controlled_rank"] for r in records]
    return {
        "seat": next(iter(seats)),
        "games": len(records),
        "seeds": [r["seed"] for r in records],
        "ranks": ranks,
        "mean_rank": statistics.mean(ranks),
        "first_rate": sum(x == 1 for x in ranks) / len(ranks),
        "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
    }


def compare_seats(groups: dict[int, list[dict]]) -> dict:
    if set(groups) != set(range(8)):
        raise ValueError("A complete seat sweep requires exactly seats 0..7")
    if not groups[0]:
        raise ValueError("At least one held-out seed is required")
    reference = [r["seed"] for r in groups[0]]
    for seat in range(8):
        if [r["seed"] for r in groups[seat]] != reference:
            raise ValueError("All seats must use exactly matching seed sequences")
    means = [summarize_seat(groups[s]) for s in range(8)]
    baseline = [r["controlled_rank"] for r in groups[0]]
    per_seed = [
        {"seed": seed,
         "controlled_seat_ranks": [groups[seat][i]["controlled_rank"] for seat in range(8)]}
        for i, seed in enumerate(reference)
    ]
    for item in per_seed:
        ranks = item["controlled_seat_ranks"]
        item["rank_range"] = max(ranks) - min(ranks)
        item["distinct_ranks"] = len(set(ranks))
    return {
        "baseline_seat": 0,
        "seed_count": len(reference),
        "matches": len(reference) * 8,
        "by_seat": means,
        "seat_mean_deltas_vs_seat0": [
            means[seat]["mean_rank"] - means[0]["mean_rank"] for seat in range(8)
        ],
        "per_seed": per_seed,
        "seeds_with_nonidentical_seat_ranks": sum(
            x["distinct_ranks"] > 1 for x in per_seed
        ),
        "matched_seat0_ranks": baseline,
    }


def run_sweep(agent_id: str, canary_seed: int, heldout_seeds: list[int],
              out_dir: Path, report_path: Path) -> dict:
    if not heldout_seeds or len(set([canary_seed] + heldout_seeds)) != len(heldout_seeds) + 1:
        raise ValueError("Independent seeds required for canary and each held-out match")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    # Mandatory independent game for this separate Round 002 candidate seat.
    canary = play(canary_seed, agent_id, controlled_seat=7)
    (out_dir / f"002-{canary_seed}.json").write_text(
        json.dumps(canary, indent=2), encoding="utf-8"
    )
    groups = {seat: [] for seat in range(8)}
    for seed in heldout_seeds:
        for seat in range(8):
            r = play(seed, agent_id, seat)
            groups[seat].append(r)
            (out_dir / f"sweep-{seed}-seat{seat}.json").write_text(
                json.dumps(r, indent=2), encoding="utf-8"
            )
    result = compare_seats(groups)
    result.update({
        "hypothesis": "The apparent seat-zero conditional result from R001 persists when rotating the same baseline through all eight seats on fresh seeds",
        "engine_version": canary["engine_version"],
        "engine_source_hash": canary["engine_source_hash"],
        "policy": "original unmodified BaselinePolicy",
        "policy_sha256": canary["policy_sha256"],
        "canary": {
            "seed": canary_seed, "controlled_seat": 7,
            "rank": canary["controlled_rank"], "decisions": canary["decisions"],
            "placements": canary["placements"],
            "turns": canary["turns"]
        },
        "total_matches_including_canary": result["matches"] + 1,
        "ppo_gradient_steps": 0,
        "model_checkpoint": None,
        "interpretation": "Descriptive seed-by-seat sensitivity; changing seat also affects hero, opponent and stochastic game trajectory. No strategy improvement or causal seat effect established.",
    })
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--agent-id", required=True)
    p.add_argument("--canary-seed", type=int, required=True)
    p.add_argument("--seeds", type=int, nargs="+", required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(
        run_sweep(a.agent_id, a.canary_seed, a.seeds, a.out_dir, a.report),
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
