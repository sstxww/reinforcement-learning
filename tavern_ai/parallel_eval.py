"""Isolated, reproducible TavernGym evaluation throughput experiment.

The same unchanged baseline policy runs one seat against seven official bots.
Process workers each instantiate their own genuine TavernGym game.
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

REPLAY_FIELDS = (
    "seed", "environment", "engine_source_hash", "engine_version",
    "agent_id", "policy", "completed", "turns", "decisions", "placements",
    "truncated_combats", "turn_limit_end", "model_sha256",
)


def _worker(task: tuple[int, str]) -> dict:
    seed, agent_id = task
    # run() validates the genuine game's termination and action legality.
    return {"receipt": run(seed, agent_id, "baseline"), "pid": os.getpid()}


def _check_parameters(games: int, workers: int) -> None:
    if not 1 <= games <= 32:
        raise ValueError("games must be between 1 and 32")
    if not 1 <= workers <= 4:
        raise ValueError("workers must be between 1 and 4")


def run_batch(seeds: list[int], agent_id: str, parallel: bool,
              workers: int = 2) -> dict:
    _check_parameters(len(seeds), workers)
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must be unique within a batch")
    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid agent id")
    tasks = [(seed, agent_id) for seed in seeds]
    start = time.perf_counter()
    if parallel:
        # Explicit spawn isolates native engine state across workers.
        ctx = multiprocessing.get_context("spawn")
        with ProcessPoolExecutor(max_workers=workers, mp_context=ctx) as pool:
            outcomes = list(pool.map(_worker, tasks))
    else:
        outcomes = [_worker(task) for task in tasks]
    elapsed = time.perf_counter() - start
    return {
        "records": [x["receipt"] for x in outcomes],
        "worker_pids": sorted({x["pid"] for x in outcomes}),
        "elapsed_seconds": elapsed,
        "games_per_second": len(seeds) / elapsed,
    }


def compare_receipts(serial: list[dict], parallel: list[dict]) -> None:
    if len(serial) != len(parallel):
        raise ValueError("Different batch lengths")
    for a, b in zip(serial, parallel, strict=True):
        mismatches = [name for name in REPLAY_FIELDS if a.get(name) != b.get(name)]
        if mismatches:
            raise ValueError(f"Seed {a.get('seed')} mismatch in {mismatches}")


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def experiment(agent_id: str, receipt_seed: int, first_seed: int, games: int,
               workers: int, experiments_dir: Path, report_path: Path) -> dict:
    _check_parameters(games, workers)
    seeds = list(range(first_seed, first_seed + games))
    if receipt_seed in seeds:
        raise ValueError("Mandatory match must have an independent seed")
    engine = verify_engine()
    own = run(receipt_seed, agent_id, "baseline")
    _save_json(experiments_dir / f"001-{receipt_seed}.json", own)
    serial = run_batch(seeds, agent_id, parallel=False, workers=workers)
    concurrent = run_batch(seeds, agent_id, parallel=True, workers=workers)
    for kind, batch in (("serial", serial), ("process", concurrent)):
        for record in batch["records"]:
            _save_json(experiments_dir / f"001-{record['seed']}-{kind}.json", record)
    compare_receipts(serial["records"], concurrent["records"])
    baseline_source = Path(__file__).with_name("baseline.py")
    implementation_hash = hashlib.sha256(
        baseline_source.read_bytes() + Path(__file__).read_bytes()
    ).hexdigest()
    result = {
        "schema": 1, "experiment": "paired_process_throughput",
        "agent_id": agent_id, "git_sha": os.getenv("GITHUB_SHA", ""),
        "run_url": (
            f"https://github.com/{os.getenv('GITHUB_REPOSITORY', '')}/actions/runs/"
            f"{os.getenv('GITHUB_RUN_ID', '')}"
            if os.getenv("GITHUB_RUN_ID") else None
        ),
        "engine": engine, "model": None, "training_steps": 0,
        "policy": "unmodified V0 baseline", "policy_runner_sha256": implementation_hash,
        "own_match": own,
        "seeds": seeds, "workers": workers,
        "serial": {
            "summary": summarize(serial["records"]),
            "elapsed_seconds": serial["elapsed_seconds"],
            "games_per_second": serial["games_per_second"],
            "worker_pids": serial["worker_pids"],
        },
        "process": {
            "summary": summarize(concurrent["records"]),
            "elapsed_seconds": concurrent["elapsed_seconds"],
            "games_per_second": concurrent["games_per_second"],
            "worker_pids": concurrent["worker_pids"],
        },
        "speedup_serial_over_process": (
            serial["elapsed_seconds"] / concurrent["elapsed_seconds"]
        ),
        "identical_replay_fields": list(REPLAY_FIELDS),
        "all_replays_identical": True,
        "limitations": "One sequential-first paired run; wall time includes process startup; "
                       "no strength improvement tested or implied.",
    }
    _save_json(report_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--receipt-seed", type=int, default=28700)
    parser.add_argument("--start-seed", type=int, default=28701)
    parser.add_argument("--games", type=int, default=6)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--receipt-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = experiment(args.agent_id, args.receipt_seed,
                        args.start_seed, args.games, args.workers,
                        args.receipt_dir, args.report)
    print(json.dumps({
        "own_rank": result["own_match"]["placements"][0],
        "games_per_arm": args.games,
        "serial_mean_rank": result["serial"]["summary"]["mean_placement"],
        "process_mean_rank": result["process"]["summary"]["mean_placement"],
        "speedup": result["speedup_serial_over_process"],
        "all_replays_identical": result["all_replays_identical"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
