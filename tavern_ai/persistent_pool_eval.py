"""Round 002: amortized process pools versus serial and per-batch spawn.

Every observation is a genuine TavernGym Game-based canary match. No mock
simulators or policy alterations are used in the benchmark.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from .canary import run
from .contract import verify_engine
from .evaluate import summarize
from .parallel_eval import _worker, compare_receipts

BATCHES = 4
SEEDS_PER_BATCH = 16
WORKERS = 2


def make_batches(start_seed: int) -> list[list[int]]:
    if start_seed < 0:
        raise ValueError("Seed must not be negative")
    return [
        list(range(start_seed + i * SEEDS_PER_BATCH,
                   start_seed + (i + 1) * SEEDS_PER_BATCH))
        for i in range(BATCHES)
    ]


def run_mode(batches: list[list[int]], agent_id: str, mode: str) -> dict:
    if mode not in {"serial", "fresh", "persistent"}:
        raise ValueError("Unknown execution mode")
    if len(batches) != BATCHES or any(len(b) != SEEDS_PER_BATCH for b in batches):
        raise ValueError("Expected four fixed 16-seed batches")
    tasks = [[(s, agent_id) for s in batch] for batch in batches]
    started = time.perf_counter()
    outcomes = []
    if mode == "serial":
        for group in tasks:
            outcomes.extend(_worker(task) for task in group)
    elif mode == "fresh":
        for group in tasks:
            with ProcessPoolExecutor(max_workers=WORKERS,
                                     mp_context=multiprocessing.get_context("spawn")) as pool:
                outcomes.extend(pool.map(_worker, group))
    else:
        # This pool persists across four independent task submissions.
        with ProcessPoolExecutor(max_workers=WORKERS,
                                 mp_context=multiprocessing.get_context("spawn")) as pool:
            for group in tasks:
                outcomes.extend(pool.map(_worker, group))
    elapsed = time.perf_counter() - started
    records = [x["receipt"] for x in outcomes]
    return {
        "records": records,
        "elapsed_seconds": elapsed,
        "worker_pids": sorted({x["pid"] for x in outcomes}),
        "games_per_second": len(records) / elapsed,
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def experiment(agent_id: str, own_seed: int, start_seeds: tuple[int, int],
               receipt_dir: Path, report_path: Path) -> dict:
    all_seeds = [seed for s in start_seeds for group in make_batches(s) for seed in group]
    if own_seed in all_seeds or len(all_seeds) != len(set(all_seeds)):
        raise ValueError("Overlapping benchmark and mandatory-game seeds")
    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid agent id")
    engine = verify_engine()
    own = run(own_seed, agent_id, "baseline")
    write_json(receipt_dir / f"002-{own_seed}.json", own)
    trials = []
    for trial, start in enumerate(start_seeds):
        batches = make_batches(start)
        order = ("serial", "fresh", "persistent") if trial == 0 else (
            "persistent", "fresh", "serial"
        )
        outcomes = {mode: run_mode(batches, agent_id, mode) for mode in order}
        serial = outcomes["serial"]["records"]
        for mode in ("fresh", "persistent"):
            compare_receipts(serial, outcomes[mode]["records"])
            # Save small genuine representative receipts, not hundreds of
            # redundant full JSON copies.
            write_json(receipt_dir / f"002-{trial + 1}-{mode}.json",
                       outcomes[mode]["records"][0])
        write_json(receipt_dir / f"002-{trial + 1}-serial.json", serial[0])
        trials.append({
            "trial": trial + 1, "seeds": [s for group in batches for s in group],
            "mode_order": list(order), "matching_game_fields": True,
            "arms": {
                mode: {
                    "elapsed_seconds": outcomes[mode]["elapsed_seconds"],
                    "games_per_second": outcomes[mode]["games_per_second"],
                    "worker_pids": outcomes[mode]["worker_pids"],
                    "summary": summarize(outcomes[mode]["records"]),
                } for mode in ("serial", "fresh", "persistent")
            },
        })
    totals = {
        mode: sum(t["arms"][mode]["elapsed_seconds"] for t in trials)
        for mode in ("serial", "fresh", "persistent")
    }
    source_sha = hashlib.sha256(
        Path(__file__).read_bytes()
        + Path(__file__).with_name("parallel_eval.py").read_bytes()
        + Path(__file__).with_name("baseline.py").read_bytes()
    ).hexdigest()
    report = {
        "schema": 1, "experiment": "persistent_pool_amortization",
        "agent_id": agent_id, "engine": engine,
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "run_url": (
            "https://github.com/" + os.getenv("GITHUB_REPOSITORY", "")
            + "/actions/runs/" + os.getenv("GITHUB_RUN_ID", "")
            if os.getenv("GITHUB_RUN_ID") else None
        ),
        "policy": "unchanged V0 BaselinePolicy",
        "policy_runner_sha256": source_sha,
        "model_sha256": None, "ppo_training_steps": 0,
        "total_real_matches": 1 + 2 * BATCHES * SEEDS_PER_BATCH * 3,
        "own_match": own, "trials": trials,
        "total_seconds": totals,
        "persistent_vs_serial_speed_ratio": totals["serial"] / totals["persistent"],
        "fresh_vs_serial_speed_ratio": totals["serial"] / totals["fresh"],
        "replay_equivalence": True,
        "limitations": "Two opposite-order trials, short native matches. "
                       "This is an engineering timing study, not policy-strength evidence.",
    }
    write_json(report_path, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--own-seed", type=int, default=28800)
    parser.add_argument("--start-seeds", type=int, nargs=2, default=[28801, 28901])
    parser.add_argument("--receipt-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = experiment(args.agent_id, args.own_seed, tuple(args.start_seeds),
                        args.receipt_dir, args.report)
    print(json.dumps({
        "total_real_matches": result["total_real_matches"],
        "own_rank": result["own_match"]["placements"][0],
        "seconds": result["total_seconds"],
        "persistent_vs_serial_speed_ratio": result["persistent_vs_serial_speed_ratio"],
        "replay_equivalence": result["replay_equivalence"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
