"""Auditable Release checkpoint inventory and CPU inference verification.

An entry is a published candidate until its bytes have been checked. This tool
never promotes a Champion or equates a load test with successful continuation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SHA256 = re.compile(r"^[0-9a-f]{64}$")
ROLES = {"unverified", "challenger", "latest", "population", "rejected", "champion"}
RELEASE_ROOT = "https://github.com/sstxww/reinforcement-learning/releases/download/"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_registry(payload: dict) -> dict:
    if type(payload) is not dict or payload.get("schema") != 1:
        raise ValueError("Unsupported checkpoint registry schema")
    entries = payload.get("entries")
    if type(entries) is not list:
        raise ValueError("Registry entries must be a list")
    ids = set()
    champions = []
    for entry in entries:
        if type(entry) is not dict:
            raise ValueError("Malformed model entry")
        model_id = entry.get("model_id")
        if not isinstance(model_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{1,120}", model_id):
            raise ValueError("Invalid model id")
        if model_id in ids:
            raise ValueError("Duplicate model id")
        ids.add(model_id)
        if entry.get("role") not in ROLES:
            raise ValueError("Unknown model role")
        if not isinstance(entry.get("model_sha256"), str) or not SHA256.fullmatch(entry["model_sha256"]):
            raise ValueError("Missing immutable weight digest")
        if type(entry.get("training_steps")) is not int or entry["training_steps"] < 0:
            raise ValueError("Invalid training steps")
        if not isinstance(entry.get("release_url"), str) or not entry["release_url"].startswith(RELEASE_ROOT):
            raise ValueError("Model weight URL must be a project GitHub Release")
        if entry.get("role") == "champion":
            verification = entry.get("verification", {})
            required = ("hash", "load", "inference", "resume", "full_game", "independent_evaluation")
            if any(verification.get(k) is not True for k in required):
                raise ValueError("Champion lacks mandatory verification gates")
            champions.append(model_id)
    champion_id = payload.get("champion_id")
    if champion_id is not None and champion_id not in champions:
        raise ValueError("Champion pointer must reference verified Champion role")
    if len(champions) > 1 or (champions and champion_id != champions[0]):
        raise ValueError("Registry may have only one verified Champion")
    latest_id = payload.get("latest_resumable_id")
    if latest_id is not None:
        choices = {e["model_id"]: e for e in entries}
        if latest_id not in choices:
            raise ValueError("Latest checkpoint not found")
        checks = choices[latest_id].get("verification", {})
        if checks.get("hash") is not True or checks.get("resume") is not True:
            raise ValueError("Latest checkpoint is not verified resumable")
    return payload


def verify_release(entry: dict, model_file: Path, metadata_file: Path, *, cpu_smoke: bool = False, seed: int = 86241) -> dict:
    if not model_file.is_file() or not metadata_file.is_file():
        raise FileNotFoundError("Release model and metadata files are both required")
    found = file_sha256(model_file)
    if found != entry["model_sha256"]:
        raise ValueError("Release model SHA256 mismatch")
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    if metadata.get("algorithm") != "MaskablePPO":
        raise ValueError("Unexpected model algorithm")
    if metadata.get("total_timesteps") != entry["training_steps"]:
        raise ValueError("Training step mismatch")
    if metadata.get("engine", {}).get("source_hash") != entry["engine_source_hash"]:
        raise ValueError("Checkpoint environment mismatch")
    report = {
        "model_id": entry["model_id"],
        "model_sha256": found,
        "hash_verified": True,
        "metadata_compatible": True,
        "cpu_load_verified": False,
        "legal_inference_verified": False,
        "resume_verified": False,
        "full_game_verified": False,
        "champion_promoted": False,
    }
    if cpu_smoke:
        from sb3_contrib import MaskablePPO
        from .contract import verify_engine
        from .env import TavernEnv
        engine = verify_engine()
        if metadata["engine"] != engine:
            raise ValueError("Release differs from installed engine contract")
        env = TavernEnv(seed=seed)
        try:
            model = MaskablePPO.load(str(model_file), env=env, device="cpu")
            report["cpu_load_verified"] = True
            obs, _ = env.reset(seed=seed)
            mask = env.action_masks()
            action, _ = model.predict(obs, action_masks=mask, deterministic=True)
            index = int(action)
            if index < 0 or index >= len(mask) or not mask[index]:
                raise ValueError("Model predicted illegal action")
            report["legal_inference_verified"] = True
            report["first_action"] = index
        finally:
            env.close()
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--model-id")
    parser.add_argument("--model", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--cpu-smoke", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    registry = validate_registry(json.loads(args.registry.read_text(encoding="utf-8")))
    if args.model_id:
        candidates = [e for e in registry["entries"] if e["model_id"] == args.model_id]
        if len(candidates) != 1:
            raise ValueError("Requested model not in registry")
        if args.model is None or args.metadata is None:
            raise ValueError("Model and metadata files required for verification")
        result = verify_release(candidates[0], args.model, args.metadata, cpu_smoke=args.cpu_smoke)
    else:
        result = {"schema": 1, "entries": len(registry["entries"]), "champion_id": registry["champion_id"], "validated": True}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
