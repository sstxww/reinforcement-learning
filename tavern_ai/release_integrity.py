"""Read-only Release lineage preflight and bounded real optimizer-resume audit.

The official train.py is not modified. This module verifies an existing
unpromoted candidate before a controlled 128-step compatibility experiment.
No model is promoted, and temporary audit output is not durable storage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .contract import (
    ACTIONS, CARDS, CATALOG_SHA256, ENGINE_HASH, FEATURES,
    PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT, verify_engine,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_source(
    model: Path,
    metadata: Path,
    expected_model_sha: str,
    expected_metadata_sha: str,
) -> dict:
    """Verify bytes + schema-2 training lineage before any library load."""
    if not model.is_file() or not metadata.is_file():
        raise FileNotFoundError("Both Release model.zip and model.metadata.json are required")
    model_hash = sha256_file(model)
    meta_hash = sha256_file(metadata)
    if model_hash != expected_model_sha or meta_hash != expected_metadata_sha:
        raise ValueError("Release asset SHA256 mismatch; refusing recovery")
    try:
        record = json.loads(metadata.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise ValueError("Unreadable checkpoint metadata") from exc
    if not isinstance(record, dict) or record.get("schema") != 2:
        raise ValueError("Schema-2 checkpoint metadata required; never silently migrate")
    if record.get("checkpoint_sha256") != model_hash:
        raise ValueError("Metadata disagrees with Release model SHA256")
    if record.get("algorithm") != "MaskablePPO":
        raise ValueError("Unsupported checkpoint algorithm")
    steps = record.get("total_timesteps")
    if type(steps) is not int or steps <= 0:
        raise ValueError("Checkpoint has no credible accumulated PPO steps")
    engine = record.get("engine")
    if not isinstance(engine, dict):
        raise ValueError("Missing pinned engine contract")
    expected = {
        "version": "1.1.0",
        "source_hash": ENGINE_HASH,
        "features": FEATURES,
        "cards": CARDS,
        "actions": ACTIONS,
    }
    for key, value in expected.items():
        if engine.get(key) != value:
            raise ValueError(f"Checkpoint engine mismatch: {key}")
    if type(engine.get("n_cards")) is not int or engine["n_cards"] <= 0:
        raise ValueError("Missing card vocabulary size")
    compatible = record.get("compatibility")
    if not isinstance(compatible, dict) or compatible.get("engine") != engine:
        raise ValueError("Missing full pinned engine compatibility manifest")
    for key, expected_value in {
        "catalog_sha256": CATALOG_SHA256,
        "ruleset_id": RULESET_ID,
        "patch_sha256": PATCH_SHA256,
        "upstream_commit": UPSTREAM_COMMIT,
    }.items():
        if compatible.get(key) != expected_value:
            raise ValueError(f"Checkpoint compatibility mismatch: {key}")
    return record


def audit_resume(
    model: Path,
    metadata: Path,
    expected_model_sha: str,
    expected_metadata_sha: str,
    output: Path,
    report: Path,
    *,
    steps: int = 128,
    seed: int = 927102,
) -> dict:
    if steps != 128:
        raise ValueError("This independent preflight permits exactly 128 PPO steps")
    previous = verify_source(model, metadata, expected_model_sha, expected_metadata_sha)
    live_engine = verify_engine()
    if live_engine != previous["engine"]:
        raise ValueError("Native engine does not exactly match saved checkpoint")
    from sb3_contrib import MaskablePPO
    import torch
    from .env import TavernEnv

    torch.set_num_threads(1)
    environment = TavernEnv(seed=seed)
    try:
        learner = MaskablePPO.load(str(model), env=environment, device="cpu")
        before = int(learner.num_timesteps)
        if before != previous["total_timesteps"]:
            raise ValueError("Loaded PPO steps disagree with checkpoint metadata")
        observation, _ = environment.reset(seed=seed)
        legal = environment.action_masks()
        action, _ = learner.predict(observation, action_masks=legal, deterministic=True)
        if not legal[int(action)]:
            raise ValueError("Restored policy predicted an illegal action")
        learner.learn(total_timesteps=steps, reset_num_timesteps=False)
        after = int(learner.num_timesteps)
        if after <= before or after - before < steps:
            raise RuntimeError("PPO optimizer did not continue for the requested steps")
        output.parent.mkdir(parents=True, exist_ok=True)
        learner.save(str(output))
        output_hash = sha256_file(output)
        updated = dict(previous)
        updated.update({
            "schema": 2, "checkpoint_sha256": output_hash,
            "total_timesteps": after, "increment_timesteps": after - before,
            "parent_checkpoint_sha256": expected_model_sha,
            "audit_only_not_promoted": True,
        })
        output.with_suffix(".metadata.json").write_text(
            json.dumps(updated, indent=2) + "\n", encoding="utf-8"
        )
        result = {
            "schema": 1, "status": "resume_smoke_verified",
            "source_release_tag": "v2-learning-41413557445",
            "source_sha256": expected_model_sha,
            "source_metadata_sha256": expected_metadata_sha,
            "resumed_sha256": output_hash,
            "initial_total_timesteps": before,
            "final_total_timesteps": after,
            "actual_added_steps": after - before,
            "loaded_and_predicted_legal_action": True,
            "engine": live_engine,
            "temporary_checkpoint": str(output),
            "promoted_to_champion": False,
            "durable_resumed_checkpoint": False,
            "next_gate": "independent completed model-controlled eight-seat game",
        }
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result
    finally:
        environment.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--expected-model-sha", required=True)
    parser.add_argument("--expected-metadata-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=128)
    parser.add_argument("--seed", type=int, default=927102)
    options = parser.parse_args()
    print(json.dumps(audit_resume(
        options.model, options.metadata,
        options.expected_model_sha, options.expected_metadata_sha,
        options.output, options.report, steps=options.steps, seed=options.seed
    ), ensure_ascii=False))


if __name__ == "__main__":
    main()
