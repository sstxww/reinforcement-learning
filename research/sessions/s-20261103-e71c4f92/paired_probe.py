"""V6.1 isolated same-seed RAW PPO versus baseline real eight-seat probe.

Only tavern_ai.canary.run produces game receipts; exceptions produce separate
failure files, never synthetic placements. Not model improvement evidence.
"""
import argparse
import json
from pathlib import Path

from tavern_ai.canary import run
from tavern_ai.receipt_integrity import validate_integrity

SESSION = "s-20261103-e71c4f92"
SEED = 99385
RELEASE = "v5-s-20261102-68099929-1408-41428692617"
WEIGHTS_SHA256 = "a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632"


def receipt_path(root, mode):
    return root / f"001-{SEED}-{mode}.json"


def play(mode, root, model):
    path = receipt_path(root, mode)
    try:
        record = run(seed=SEED, agent_id=SESSION, policy=mode,
                     model_path=str(model) if mode == "model" else None)
        validate_integrity(record)
        if record["seed"] != SEED or record["policy"] != mode:
            raise ValueError("Runner returned mismatched seed or policy")
        if mode == "model" and record["model_sha256"] != WEIGHTS_SHA256:
            raise ValueError("Raw model bytes differ from the registered Release")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return record
    except Exception as exc:
        failure = {
            "kind": "failed_run_not_a_game_receipt", "session_id": SESSION,
            "seed": SEED, "policy": mode, "completed": False,
            "failure_type": type(exc).__name__, "reason": str(exc)[:1000],
            "release_tag": RELEASE if mode == "model" else None,
        }
        failure_path = root / f"001-{SEED}-{mode}-failure.json"
        failure_path.parent.mkdir(parents=True, exist_ok=True)
        failure_path.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        raise


def pair(root):
    results = {}
    for mode in ("baseline", "model"):
        results[mode] = json.loads(receipt_path(root, mode).read_text(encoding="utf-8"))
        validate_integrity(results[mode])
        if results[mode]["seed"] != SEED or results[mode]["policy"] != mode:
            raise ValueError("Nonpaired or mislabeled full game")
    if results["model"]["model_sha256"] != WEIGHTS_SHA256:
        raise ValueError("Model did not match registered Release")
    ranks = {mode: int(results[mode]["placements"][0]) for mode in results}
    report = {
        "kind": "single_seed_descriptive_paired_real_game",
        "session_id": SESSION, "seed": SEED, "controlled_seat": 0,
        "policy_mode": "raw_unassisted_no_guard_no_fallback",
        "registered_release": RELEASE, "registered_model_sha256": WEIGHTS_SHA256,
        "baseline_placement": ranks["baseline"], "model_placement": ranks["model"],
        "model_minus_baseline_placement": ranks["model"] - ranks["baseline"],
        "games_completed": 2, "sample_n_per_policy": 1,
        "training_new_steps": 0, "champion_promoted": False,
        "inference": "Descriptive pilot only; no causal or strength conclusion",
        "original_receipts": [str(receipt_path(root, m)) for m in ("baseline", "model")],
    }
    report_path = root / f"001-{SEED}-paired-summary.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "model", "pair"), required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path)
    args = parser.parse_args()
    if args.mode == "model" and args.model is None:
        parser.error("--model is required for raw model games")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.mode == "pair":
        pair(args.out_dir)
    else:
        print(json.dumps(play(args.mode, args.out_dir, args.model), sort_keys=True))


if __name__ == "__main__":
    main()
