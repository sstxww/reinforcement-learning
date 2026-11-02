"""Verify both actual saved PPO checkpoints in the immutable session Actions Artifact."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from sb3_contrib import MaskablePPO
from tavern_ai.contract import verify_engine
from tavern_ai.env import TavernEnv

SESSION = "s-20261102-24728f13"
ORIGIN_RUN = 41416467100


def run():
    report_path = Path("reports") / SESSION / "001-lr-ablation.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report["session_id"] != SESSION or report["run_sha"] != "ff2f28b76d6a484e248437bb27c868f3550827d1":
        raise ValueError("Incorrect origin run/experiment")
    if report["engine"] != verify_engine():
        raise ValueError("Checkpoint engine mismatch")
    details = {}
    for label in ("reference", "candidate"):
        expected = report["training"][label]
        path = Path(expected["checkpoint_path"])
        if not path.is_file():
            raise FileNotFoundError(f"Missing Artifact checkpoint: {path}")
        sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        if sha256 != expected["model_sha256"]:
            raise ValueError(f"Checkpoint hash mismatch for {label}")
        model = MaskablePPO.load(str(path), device="cpu")
        if not model.policy:
            raise ValueError(f"Checkpoint policy unavailable for {label}")
        env = TavernEnv(seed=42174)
        try:
            obs, _ = env.reset(seed=42174)
            mask = env.action_masks()
            predicted, _ = model.predict(obs, action_masks=mask, deterministic=True)
            action = int(np.asarray(predicted).item())
            if not 0 <= action < 245 or not bool(mask[action]):
                raise ValueError(f"Reloaded {label} predicted illegal action {action}")
            details[label] = {
                "sha256": sha256,
                "checkpoint_load_success": True,
                "legal_masked_inference": True,
                "inference_action": action,
                "model_timesteps": int(model.num_timesteps),
            }
            if details[label]["model_timesteps"] != 256:
                raise ValueError(f"Unexpected loaded training step count for {label}")
        finally:
            env.close()
    data = {
        "session_id": SESSION,
        "checkpoint_origin_run_id": ORIGIN_RUN,
        "verification_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "verification_commit": os.environ.get("GITHUB_SHA", ""),
        "engine": report["engine"],
        "status": "validated_hash_reload_and_legal_inference",
        "checkpoints": details,
        "model_state": "Candidate only, not Best; source Artifact expires 2026-12-02.",
    }
    out = Path("reports") / SESSION / "001-checkpoint-recovery.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))
    return data


if __name__ == "__main__":
    run()
