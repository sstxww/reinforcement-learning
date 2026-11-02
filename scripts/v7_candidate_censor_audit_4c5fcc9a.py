"""Offline, fail-closed audit of two distinct 1536-step candidate evidence cohorts.

Read-only: does not run agents, synthesize receipts, promote models, or mutate registry.
An incomplete evaluation has no placement, even if a separate completed match was eighth.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{64}\Z")


def _digest(value: object) -> str:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError("missing or invalid exact model SHA-256")
    return value


def _game(record: dict, *, policy: str, sha: str | None = None) -> int:
    if record.get("environment") != "TavernGym" or record.get("completed") is not True:
        raise ValueError("incomplete, non-TavernGym, or unverified game")
    if record.get("policy") != policy or record.get("engine_version") != "1.1.0":
        raise ValueError("wrong policy or engine version")
    if record.get("engine_source_hash") != "6d8712c93022ba11":
        raise ValueError("engine source hash mismatch")
    places = record.get("placements")
    if type(places) is not list or len(places) != 8 or any(type(n) is not int for n in places):
        raise ValueError("incomplete eight-seat ranking")
    if sorted(places) != list(range(1, 9)):
        raise ValueError("rankings are not a full permutation")
    if type(record.get("seed")) is not int or type(record.get("decisions")) is not int or record["decisions"] <= 0:
        raise ValueError("invalid seed or decisions")
    if record.get("truncated_combats") != 0 or record.get("turn_limit_end") is not False:
        raise ValueError("game termination guard was triggered")
    if policy == "model" and _digest(record.get("model_sha256")) != sha:
        raise ValueError("model receipt SHA mismatch")
    if policy == "baseline" and record.get("model_sha256") is not None:
        raise ValueError("baseline falsely contains model weights")
    for key in ("fallback_actions", "guard_forced_ends", "model_guard_forced_end"):
        if type(record.get(key, 0)) is not int or record.get(key, 0) != 0:
            raise ValueError("assisted/guarded model receipt")
    return places[0]


def audit(baseline: dict, parent: dict, candidate: dict, manifest: dict, failure: dict) -> dict:
    parent_sha = _digest(manifest.get("parent_sha256"))
    candidate_sha = _digest(manifest.get("candidate_sha256"))
    failed_sha = _digest(failure.get("candidate_sha256"))
    if len({parent_sha, candidate_sha, failed_sha}) != 3:
        raise ValueError("three distinct checkpoint identities required in this fixed-cohort audit")
    if manifest.get("training_steps_total") != 1536 or manifest.get("training_steps_added") != 128:
        raise ValueError("candidate step count mismatch")
    if manifest.get("storage", {}).get("durable") is not False:
        raise ValueError("candidate storage status changed; re-audit custody")
    if failure.get("candidate_training_steps") != 1536 or failure.get("candidate_heldout", {}).get("completed_report") is not False:
        raise ValueError("failed held-out cohort status changed; re-audit source")
    heldout = failure["candidate_heldout"]
    if heldout.get("any_placement_claimed") is not False or not heldout.get("error"):
        raise ValueError("failed heldout must have a concrete failure, not placement")
    if failure.get("parent_sha256") != parent_sha:
        raise ValueError("cohort parent release SHA mismatch")
    baseline_rank = _game(baseline, policy="baseline")
    parent_rank = _game(parent, policy="model", sha=parent_sha)
    candidate_rank = _game(candidate, policy="model", sha=candidate_sha)
    if baseline["seed"] != parent["seed"]:
        raise ValueError("baseline and parent games are not same seed")
    if candidate["seed"] == parent["seed"]:
        raise ValueError("candidate game is not an independent seed in this fixed audit")
    failed_seeds = heldout.get("requested_seeds")
    if not isinstance(failed_seeds, list) or not failed_seeds or any(type(x) is not int for x in failed_seeds):
        raise ValueError("failed held-out seeds not identified")
    return {
        "schema": 1,
        "audit": "historical_evidence_identity_and_censoring_only",
        "source": "existing committed real TavernGym results; no new match generated",
        "parent_sha256": parent_sha,
        "matched_parent_baseline": {"seed": parent["seed"], "baseline_rank": baseline_rank,
                                    "parent_rank": parent_rank, "parent_minus_baseline": parent_rank - baseline_rank,
                                    "pairs": 1},
        "cohorts": [
            {"sha256": candidate_sha, "training_steps": 1536, "seed": candidate["seed"],
             "complete_raw_model_game": True, "rank": candidate_rank,
             "durable_checkpoint": False, "candidate_vs_parent_matched_games": 0},
            {"sha256": failed_sha, "training_steps": 1536, "heldout_requested_seeds": failed_seeds,
             "heldout_completed": False, "heldout_rank": None,
             "failure": heldout["error"], "candidate_vs_parent_matched_games": 0}
        ],
        "combined_candidate_mean_rank": None,
        "verified_candidate_improvement": False,
        "note": "Distinct 1536-step checkpoints must not be pooled. Incomplete games have no placement."
    }


def main() -> None:
    p = argparse.ArgumentParser()
    for arg in ("baseline", "parent", "candidate", "manifest", "failure"):
        p.add_argument("--" + arg, required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    records = {key: json.loads(getattr(args, key).read_text(encoding="utf-8"))
               for key in ("baseline", "parent", "candidate", "manifest", "failure")}
    report = audit(**records)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
