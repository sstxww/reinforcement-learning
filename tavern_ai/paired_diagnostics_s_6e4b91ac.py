"""Fail-closed, failure-aware paired real-game diagnostics for one unpromoted model.

Completed canary receipts are validated before ranking. A terminated safety-limit
probe is only a failure record, NEVER a full game, rank, or fallback result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean

from .validate_receipt import validate

_SOURCE_RELEASE = "v5-s-20261102-6e4b91ac-resume128"
_EXPECTED_ENGINE = "6d8712c93022ba11"


def report_pair(seed: int, model_path: Path, runner) -> dict:
    """Use independent full real TavernGym games; do not infer missing placement."""
    row = {"seed": seed, "model": None, "baseline": None}
    for policy in ("model", "baseline"):
        try:
            result = runner(
                seed, "s-20261102-6e4b91ac", policy,
                str(model_path) if policy == "model" else None,
            )
            validate(result)
            if result.get("seed") != seed or result.get("policy") != policy:
                raise ValueError("Wrong policy arm or seed")
            if result.get("engine_source_hash") != _EXPECTED_ENGINE:
                raise ValueError("Incompatible TavernGym engine fingerprint")
            row[policy] = {
                "completed": True, "placement": result["placements"][0],
                "receipt": result,
            }
        except RuntimeError as exc:
            if "Full-game safety limit exceeded" not in str(exc):
                raise
            row[policy] = {
                "completed": False,
                "failure_code": "real_game_safety_limit_exceeded",
                "exception_type": type(exc).__name__,
                "placement": None,
                "receipt": None,
                "not_a_complete_match": True,
            }
    return row


def summarize(rows: list[dict]) -> dict:
    if len({r["seed"] for r in rows}) != len(rows):
        raise ValueError("Duplicate seeds")
    complete = [
        r for r in rows
        if r["model"] is not None and r["baseline"] is not None
        and r["model"]["completed"] and r["baseline"]["completed"]
    ]
    failed_model = [r["seed"] for r in rows if r["model"] and not r["model"]["completed"]]
    all_valid = len(rows) >= 1 and len(complete) == len(rows)
    return {
        "attempted_pairs": len(rows),
        "complete_pairs": len(complete),
        "failed_model_seeds": failed_model,
        "all_model_games_completed": all_valid,
        "mean_rank_model_complete_pairs_only": (
            mean(r["model"]["placement"] for r in complete) if complete else None
        ),
        "mean_rank_baseline_complete_pairs_only": (
            mean(r["baseline"]["placement"] for r in complete) if complete else None
        ),
        "mean_paired_rank_delta_complete_pairs_only": (
            mean(r["model"]["placement"] - r["baseline"]["placement"]
                 for r in complete) if complete else None
        ),
        "unconditional_four_game_mean_is_valid": all_valid,
        "champion_eligible": False,
        "no_competitive_improvement_claim": True,
        "incomplete_game_is_never_ranked_eighth": True,
    }


def run_diagnostic(model: Path, expected_sha: str, seeds: list[int], out: Path, runner) -> dict:
    if not 1 <= len(seeds) <= 4 or len(set(seeds)) != len(seeds):
        raise ValueError("Require one to four distinct heldout seeds")
    if not model.is_file() or len(expected_sha) != 64:
        raise ValueError("Missing model or expected pinned SHA-256")
    actual = hashlib.sha256(model.read_bytes()).hexdigest()
    if actual != expected_sha:
        raise ValueError("Model checkpoint SHA256 mismatch")
    rows = []
    out.parent.mkdir(parents=True, exist_ok=True)
    for seed in seeds:
        if type(seed) is not int or seed < 0:
            raise ValueError("Invalid game seed")
        row = report_pair(seed, model, runner)
        rows.append(row)
        payload = {
            "schema": 1,
            "session_id": "s-20261102-6e4b91ac",
            "source_release": _SOURCE_RELEASE,
            "checkpoint_sha256": actual,
            "pinned_engine_hash": _EXPECTED_ENGINE,
            "intended_seeds": seeds,
            "tested_seeds": [r["seed"] for r in rows],
            "mode": "real_eight_seat_games_with_failure_accounting",
            "no_policy_guard_or_fallback": True,
            "paired": rows,
            "summary": summarize(rows),
            "limitations": (
                "Four or fewer seeds, fixed seat 0, seven scripted bots; any incomplete "
                "game has NO placement and is excluded from all mean ranks. "
                "No causal root-cause or strength claim."
            ),
        }
        temp = out.with_suffix(out.suffix + ".tmp")
        temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temp.replace(out)
    return payload


def main() -> None:
    from .canary import run as game_run
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--start-seed", type=int, default=86410)
    p.add_argument("--games", type=int, default=4)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if not 1 <= args.games <= 4:
        p.error("games must be 1..4")
    result = run_diagnostic(
        args.model, args.expected_sha256,
        list(range(args.start_seed, args.start_seed + args.games)),
        args.out, game_run,
    )
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
