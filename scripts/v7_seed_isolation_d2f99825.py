"""Bounded per-seed raw TavernGym evaluation with preserved failure evidence.

A failure is never a placement; no guard, baseline rescue, auto-retry or promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Callable

ENGINE_HASH = "6d8712c93022ba11"


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def run_batch(
    *, session_id: str, start_seed: int, games: int, policy: str,
    out_dir: Path, model: Path | None = None, compare_baseline: bool = False,
    game_fn: Callable | None = None, validator: Callable | None = None,
) -> dict:
    if not re.fullmatch(r"s-[0-9]{8}-[0-9a-f]{8}", session_id):
        raise ValueError("Invalid isolated SESSION_ID")
    if type(start_seed) is not int or start_seed < 0 or type(games) is not int or not 1 <= games <= 4:
        raise ValueError("Require nonnegative seed and bounded games 1..4")
    if policy not in ("baseline", "model"):
        raise ValueError("Policy must be raw model or baseline")
    if compare_baseline and policy != "model":
        raise ValueError("Baseline comparison requires the raw model arm")
    expected_hash = None
    if policy == "model":
        if model is None or not model.is_file():
            raise FileNotFoundError("Raw model checkpoint is required")
        expected_hash = hashlib.sha256(model.read_bytes()).hexdigest()
    if game_fn is None:
        from tavern_ai.canary import run as game_fn
    if validator is None:
        from tavern_ai.receipt_integrity import validate_integrity as validator

    arms = ("model", "baseline") if compare_baseline else (policy,)
    outcomes: list[dict] = []
    for seed in range(start_seed, start_seed + games):
        for arm in arms:
            stem = f"{arm}-{seed}"
            try:
                record = game_fn(seed, session_id, arm, str(model) if arm == "model" else None)
                validator(record)
                if (record.get("seed") != seed or record.get("agent_id") != session_id
                    or record.get("policy") != arm or record.get("completed") is not True
                    or record.get("engine_source_hash") != ENGINE_HASH
                    or record.get("turn_limit_end") is not False
                    or record.get("truncated_combats") != 0
                    or record.get("seat", 0) != 0
                    or any(record.get(k, 0) != 0 for k in (
                        "fallback_actions", "guard_forced_ends", "guard_interventions",
                        "forced_end_count", "safety_fallback_count"))
                    or (arm == "model" and record.get("model_sha256") != expected_hash)
                    or (arm == "baseline" and record.get("model_sha256") is not None)):
                    raise ValueError("Policy, engine, seed, seat, model SHA, or raw provenance mismatch")
                rank = record["placements"][0]
                path = out_dir / "receipts" / f"{stem}.json"
                _atomic_json(path, record)
                outcomes.append({"seed": seed, "arm": arm, "completed": True,
                                 "placement": rank, "receipt": str(path)})
            except Exception as exc:
                path = out_dir / "failures" / f"{stem}.json"
                failure = {"schema": 1, "seed": seed, "arm": arm,
                           "session_id": session_id, "completed": False,
                           "error_type": type(exc).__name__,
                           "failure_signature": str(exc)[:300],
                           "model_sha256": expected_hash if arm == "model" else None,
                           "no_placement_claimed": True}
                _atomic_json(path, failure)
                outcomes.append({"seed": seed, "arm": arm, "completed": False,
                                 "failure": str(path)})
    by_arm = {}
    for arm in arms:
        rows = [x for x in outcomes if x["arm"] == arm]
        ranks = [x["placement"] for x in rows if x["completed"]]
        by_arm[arm] = {"attempted": len(rows), "completed": len(ranks),
                       "failed": len(rows) - len(ranks),
                       "placements_completed_only": ranks,
                       "mean_placement_completed_only": (sum(ranks) / len(ranks)) if ranks else None}
    paired = None
    if compare_baseline:
        m = {x["seed"]: x["placement"] for x in outcomes if x["arm"] == "model" and x["completed"]}
        b = {x["seed"]: x["placement"] for x in outcomes if x["arm"] == "baseline" and x["completed"]}
        pairs = sorted(set(m) & set(b))
        paired = {"fully_completed_pairs": len(pairs), "seeds": pairs,
                  "mean_model_minus_baseline": (sum(m[s] - b[s] for s in pairs) / len(pairs)) if pairs else None}
    all_done = all(x["completed"] for x in outcomes)
    result = {"schema": 1, "session_id": session_id, "status": "complete" if all_done else "failed_with_evidence",
              "source_model_sha256": expected_hash, "policy_provenance": "raw model, no guard or fallback",
              "requested_seeds": list(range(start_seed, start_seed + games)), "by_arm": by_arm,
              "paired_complete_only": paired, "outcomes": outcomes,
              "promotion_authorized": False}
    _atomic_json(out_dir / "summary.json", result)
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--session-id", required=True)
    p.add_argument("--start-seed", required=True, type=int)
    p.add_argument("--games", type=int, default=1)
    p.add_argument("--policy", choices=("baseline", "model"), required=True)
    p.add_argument("--model", type=Path)
    p.add_argument("--compare-baseline", action="store_true")
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args(argv)
    report = run_batch(session_id=args.session_id, start_seed=args.start_seed,
                       games=args.games, policy=args.policy, model=args.model,
                       compare_baseline=args.compare_baseline, out_dir=args.out_dir)
    print(json.dumps({"status": report["status"], "by_arm": report["by_arm"],
                      "paired": report["paired_complete_only"]}, ensure_ascii=False))
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
