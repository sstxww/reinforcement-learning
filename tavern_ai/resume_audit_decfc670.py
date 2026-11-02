"""Bounded real PPO continuation audit from a checksum-verified existing Release.

No promise of strength gain; verifies optimizer counters and exact step count.
Only writes session-owned paths, never changes Champion or Latest automatically.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .checkpoint_registry import file_sha256, validate_registry, verify_release


def optimizer_step(model) -> int:
    """Read Adam update counter; zero means no tracked optimizer updates."""
    steps = []
    for state in model.policy.optimizer.state.values():
        count = state.get("step")
        if count is not None:
            steps.append(int(count.item()) if hasattr(count, "item") else int(count))
    return max(steps, default=0)


def resume_verified(
    registry: Path, source_zip: Path, source_metadata: Path,
    output_zip: Path, report_file: Path, *, steps: int = 128, seed: int = 86253
) -> dict:
    if steps != 128:
        raise ValueError("Single bounded resume audit uses exactly 128 PPO steps")
    data = validate_registry(json.loads(registry.read_text(encoding="utf-8")))
    source = next(e for e in data["entries"] if e["model_id"] == "v2-learning-41413557445")
    source_check = verify_release(source, source_zip, source_metadata, cpu_smoke=True)
    from sb3_contrib import MaskablePPO
    from .train import run as real_train

    old = MaskablePPO.load(str(source_zip), device="cpu")
    before_count = int(old.num_timesteps)
    before_opt = optimizer_step(old)
    if before_count != source["training_steps"] or before_opt <= 0:
        raise ValueError("Missing or invalid prior timestep/optimizer state")
    del old
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    metadata = real_train(steps=steps, seed=seed, model_out=output_zip, resume=source_zip)
    metadata_path = output_zip.with_suffix(".metadata.json")
    if not output_zip.is_file() or not metadata_path.is_file():
        raise RuntimeError("Training did not persist its checkpoint and metadata")
    new = MaskablePPO.load(str(output_zip), device="cpu")
    after_count = int(new.num_timesteps)
    after_opt = optimizer_step(new)
    if after_count != before_count + steps:
        raise RuntimeError(f"Real PPO steps not reflected: {before_count} -> {after_count}")
    if after_opt <= before_opt:
        raise RuntimeError("Optimizer state did not advance during resumed PPO learning")
    if metadata["total_timesteps"] != after_count:
        raise RuntimeError("Output metadata disagrees with actual restored model")
    output_sha = file_sha256(output_zip)
    if output_sha == source["model_sha256"]:
        raise RuntimeError("Resumed weight artifact unexpectedly byte-identical")
    report = {
        "schema": 1, "kind": "real_bounded_optimizer_resume_128_steps",
        "source_model_id": source["model_id"],
        "source_model_sha256": source["model_sha256"],
        "source_hash_verified": source_check["hash_verified"],
        "source_cpu_load_verified": source_check["cpu_load_verified"],
        "source_legal_inference_verified": source_check["legal_inference_verified"],
        "old_total_timesteps": before_count,
        "new_gradient_rollout_timesteps": steps,
        "new_total_timesteps": after_count,
        "old_optimizer_step": before_opt,
        "new_optimizer_step": after_opt,
        "new_model_sha256": output_sha,
        "engine": metadata["engine"],
        "training_seed": seed,
        "new_model_cpu_load_verified": True,
        "new_model_unguarded_full_game_verified": False,
        "competitive_gain_verified": False,
        "champion_promoted": False,
    }
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("models/sessions/s-20261102-decfc670/registry.json"))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=86253)
    parser.add_argument("--steps", type=int, default=128)
    args = parser.parse_args()
    result = resume_verified(args.registry, args.source, args.metadata, args.out, args.report,
                             steps=args.steps, seed=args.seed)
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
