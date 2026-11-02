"""Publish a VERIFIED candidate checkpoint to an immutable-version GitHub Release.

The tag is unique per Actions run. This never promotes Best and never writes to
upstream or TavernArena. Use after a real model canary and independent evaluation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ALLOWED_REPO = "sstxww/reinforcement-learning"
ENGINE_HASH = "6d8712c93022ba11"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect_candidate(model: Path, metadata: Path, receipt: Path, evaluation: Path) -> dict:
    for path in (model, metadata, receipt, evaluation):
        if not path.is_file():
            raise FileNotFoundError(f"Missing required candidate evidence: {path}")
    m = json.loads(metadata.read_text(encoding="utf-8"))
    r = json.loads(receipt.read_text(encoding="utf-8"))
    e = json.loads(evaluation.read_text(encoding="utf-8"))
    digest = sha256(model)
    if m.get("checkpoint_sha256") != digest:
        raise ValueError("Model hash differs from training checkpoint metadata")
    engine = m.get("engine", {})
    if engine.get("version") != "1.1.0" or engine.get("source_hash") != ENGINE_HASH:
        raise ValueError("Checkpoint environment incompatible with pinned TavernGym")
    if not m.get("compatibility") or m["compatibility"].get("engine") != engine:
        raise ValueError("Incomplete checkpoint compatibility manifest")
    if type(m.get("total_timesteps")) is not int or m["total_timesteps"] <= 0:
        raise ValueError("Missing real training steps")
    if (r.get("environment"), r.get("completed"), r.get("agent_id"), r.get("policy")) != (
        "TavernGym", True, "learning", "model"
    ):
        raise ValueError("Missing completed model-controlled learning match")
    if r.get("model_sha256") != digest or r.get("engine_source_hash") != ENGINE_HASH:
        raise ValueError("Canary used a different model or simulator")
    if (r.get("truncated_combats") or r.get("turn_limit_end")
        or len(r.get("placements", [])) != 8):
        raise ValueError("Model match was not a complete eight-seat game")
    # Both current evaluation layouts report an explicit nonzero game count.
    metrics = e.get("metrics", e.get("candidate", e))
    if type(metrics.get("games")) is not int or metrics["games"] < 1:
        raise ValueError("No independent evaluation games found")
    return {
        "schema": 1, "role": "candidate", "promoted_to_best": False,
        "repository": ALLOWED_REPO, "checkpoint_sha256": digest,
        "metadata_sha256": sha256(metadata), "receipt_sha256": sha256(receipt),
        "evaluation_sha256": sha256(evaluation),
        "engine": engine, "compatibility": m["compatibility"],
        "total_timesteps": m["total_timesteps"],
        "evaluation_games": metrics["games"],
        "model_game_seed": r["seed"], "model_game_placement": r["placements"][0],
        "warning": "Candidate only: independent multi-game promotion review required.",
    }

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--evaluation", type=Path, required=True)
    p.add_argument("--tag", required=True)
    p.add_argument("--target", required=True, help="Actual checked-out learning commit SHA")
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--publish", action="store_true", help="Requires GH_TOKEN and GitHub Actions")
    a = p.parse_args()
    if not re.fullmatch(r"autotavern-v1-candidate-[0-9]+", a.tag):
        p.error("Tag must be a unique run-number candidate tag")
    if not re.fullmatch(r"[a-f0-9]{40}", a.target):
        p.error("Target must be a full, pinned Git commit SHA")
    manifest = inspect_candidate(a.model, a.metadata, a.receipt, a.evaluation)
    manifest.update({"tag": a.tag, "target_commit": a.target,
                     "release_url": f"https://github.com/{ALLOWED_REPO}/releases/tag/{a.tag}"})
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if not a.publish:
        print("Verified candidate manifest; publication not requested.")
        return
    if not os.getenv("GH_TOKEN"):
        raise RuntimeError("GH_TOKEN required for publishing to the permitted repository")
    subprocess.run(
        ["gh", "release", "create", a.tag, "--repo", ALLOWED_REPO,
         "--target", a.target, "--prerelease",
         "--title", f"AutoTavern V1 candidate {a.tag}",
         "--notes", "Unpromoted checkpoint. Verify model hash, environment, and evaluation manifest.",
         str(a.model), str(a.metadata), str(a.receipt), str(a.evaluation),
         str(a.manifest)],
        check=True,
    )
    print(f"Candidate release published: {manifest['release_url']}")

if __name__ == "__main__":
    main()
