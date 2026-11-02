#!/usr/bin/env python3
"""One bounded, unassisted, same-seed 1408-step PPO versus baseline probe.

Does not rescue a stuck model, fabricate a rank, train, or promote checkpoints.
An exception produces a FAILURE record, never a completed game receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import traceback
from pathlib import Path


def require_complete(record: dict, *, seed: int, policy: str,
                     expected_model_sha: str | None = None) -> None:
    """Fail closed on provenance and a genuine eight-seat placement permutation."""
    if record.get("seed") != seed or record.get("policy") != policy:
        raise ValueError("Seed/policy identity mismatch")
    if record.get("completed") is not True or record.get("turn_limit_end") is not False:
        raise ValueError("Not a naturally completed game")
    if record.get("truncated_combats") != 0 or record.get("fallback_actions", 0) != 0:
        raise ValueError("Truncated or fallback-assisted game")
    if record.get("guard_forced_ends", 0) != 0:
        raise ValueError("Guard-assisted game")
    if record.get("placements") is None or sorted(record["placements"]) != list(range(1, 9)):
        raise ValueError("Placements are not an eight-seat permutation")
    if policy == "model" and record.get("model_sha256") != expected_model_sha:
        raise ValueError("The model game did not use the registered checkpoint")
    if policy == "baseline" and record.get("model_sha256") is not None:
        raise ValueError("Baseline receipt unexpectedly identifies weights")


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                    encoding="utf-8")


def probe(seed: int, model_path: Path, registry_path: Path,
          agent_id: str, output_dir: Path) -> bool:
    from tavern_ai.canary import run
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    source = registry["latest"]
    actual_sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if actual_sha != source["checkpoint_sha256"]:
        raise ValueError("Read-only model bytes differ from registered release")
    result = {"schema": 1, "seed": seed, "controlled_seat": 0,
              "source_model_id": source["id"], "model_sha256": actual_sha,
              "source_steps": source["training_steps"], "new_ppo_steps": 0,
              "policy_mode": "raw deterministic PPO, no guard or fallback",
              "opponents": "seven TavernGym scripted bots",
              "model": {"status": "not_run"}, "baseline": {"status": "not_run"}}
    for policy in ("model", "baseline"):
        try:
            record = run(seed, agent_id, policy,
                         str(model_path) if policy == "model" else None)
            require_complete(record, seed=seed, policy=policy,
                             expected_model_sha=actual_sha if policy == "model" else None)
            path = output_dir / f"001-{seed}-{policy}.json"
            save_json(path, record)
            result[policy] = {"status": "completed", "rank": record["placements"][0],
                              "receipt": str(path), "decisions": record["decisions"]}
            print(json.dumps({"policy": policy, "genuine_receipt": record},
                             ensure_ascii=False), flush=True)
        except Exception as exc:
            # Do NOT convert an unfinished raw PPO game to eighth place.
            result[policy] = {"status": "failed", "completed": False,
                              "rank": None, "error_type": type(exc).__name__,
                              "error": str(exc)[:600]}
            failure_path = output_dir / f"001-{seed}-{policy}-failure.json"
            save_json(failure_path, {"seed": seed, "policy": policy,
                                    "source_model_sha256": actual_sha,
                                    **result[policy],
                                    "traceback": traceback.format_exc()[-5000:]})
            print(json.dumps({"failed_game": result[policy]}), flush=True)
    if result["model"]["status"] == result["baseline"]["status"] == "completed":
        result["model_minus_baseline_rank"] = (
            result["model"]["rank"] - result["baseline"]["rank"])
        result["n_paired_seeds"] = 1
    else:
        result["model_minus_baseline_rank"] = None
        result["n_paired_seeds"] = 0
    save_json(output_dir / f"001-{seed}-status.json", result)
    print(json.dumps({"paired_status": result}, ensure_ascii=False), flush=True)
    return result["model"]["status"] == result["baseline"]["status"] == "completed"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--agent-id", required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    if not probe(a.seed, a.model, a.registry, a.agent_id, a.out_dir):
        raise SystemExit("Uncompleted model/baseline game; see failure record (NOT a rank)")


if __name__ == "__main__":
    main()
