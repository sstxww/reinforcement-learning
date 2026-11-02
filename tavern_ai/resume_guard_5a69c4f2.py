"""V5 fail-closed, read-only recovery of one registered durable PPO Release.

This is an integration preflight, not a training command or Champion promotion.
No network retrieval occurs until the exact allowed registry entry is checked.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

from .checkpoint_preflight import audit_archive, probe_inference

REPOSITORY = "sstxww/reinforcement-learning"
TAG = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
SHA256 = re.compile(r"[a-f0-9]{64}")


def select_release(registry: dict, role: str = "latest") -> dict:
    if role not in ("latest", "best"):
        raise ValueError("Only explicit latest or best roles are supported")
    if not isinstance(registry, dict) or registry.get("repository") != REPOSITORY:
        raise ValueError("Wrong source repository or malformed registry")
    entry = registry.get(role)
    if not isinstance(entry, dict):
        raise ValueError(f"No registered {role} checkpoint; refuse silent fresh start")
    digest = entry.get("checkpoint_sha256")
    tag = entry.get("release_tag")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        raise ValueError("Missing trusted lower-case checkpoint SHA256")
    if not isinstance(tag, str) or not TAG.fullmatch(tag):
        raise ValueError("Invalid registered Release tag")
    if entry.get("durable_storage") != "github_release":
        raise ValueError("Checkpoint is not registered as durable GitHub Release")
    if entry.get("model_asset") != "model.zip" or entry.get("metadata_asset") != "model.metadata.json":
        raise ValueError("Unexpected Release asset filenames")
    if entry.get("release") != f"https://github.com/{REPOSITORY}/releases/tag/{tag}":
        raise ValueError("Registered Release identity mismatch")
    if type(entry.get("training_steps")) is not int or entry["training_steps"] <= 0:
        raise ValueError("Missing cumulative trained steps")
    if not entry.get("release_download_sha256_verified") or not entry.get("model_load_verified"):
        raise ValueError("Source Release lacks verified download/load custody")
    if role == "best" and not entry.get("promoted_to_best"):
        raise ValueError("Unpromoted checkpoint cannot become the Best role")
    return entry


def restore_registered(
    registry_path: Path, destination: Path, role: str = "latest",
    *, inference: bool = False, downloader=None,
) -> dict:
    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    entry = select_release(registry, role)
    destination = Path(destination)
    target_zip = destination / "model.zip"
    target_meta = destination / "model.metadata.json"
    target_attestation = destination / "source-attestation.json"
    if any(p.exists() for p in (target_zip, target_meta, target_attestation)):
        raise FileExistsError("Refusing to overwrite existing checkpoint or custody record")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tavern-v5-source-", dir=destination.parent) as stage_name:
        stage = Path(stage_name)
        command = [
            "gh", "release", "download", entry["release_tag"], "--repo", REPOSITORY,
            "--dir", str(stage), "--pattern", "model.zip",
            "--pattern", "model.metadata.json",
        ]
        if downloader is None:
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            if completed.returncode:
                raise RuntimeError("Registered Release download failed; refusing fresh initialization")
        else:
            downloader(command, stage)
        archive = stage / "model.zip"
        metadata = stage / "model.metadata.json"
        if archive.is_symlink() or metadata.is_symlink():
            raise ValueError("Symlink Release assets not permitted")
        audited = audit_archive(archive, metadata, entry["checkpoint_sha256"])
        if audited["total_timesteps"] != entry["training_steps"]:
            raise ValueError("Registry/Release cumulative step count mismatch")
        if inference:
            probe_inference(archive)
        result = {
            "schema": 1, "repository": REPOSITORY, "role": role,
            "checkpoint_id": entry["id"], "release_tag": entry["release_tag"],
            "sha256": audited["sha256"], "total_timesteps": audited["total_timesteps"],
            "metadata_schema": audited["checkpoint_metadata_schema"],
            "archive_integrity": "passed",
            "engine_compatibility": "passed",
            "model_inference": "passed_one_action" if inference else "not_tested",
            "optimizer_continuation_from_this_copy": "not_tested",
            "new_training_steps": 0, "competitive_improvement": "not_established",
            "promoted_to_champion": False,
        }
        destination.mkdir(parents=True, exist_ok=True)
        # Copy only after ALL checks pass. Never silently substitute random weights.
        target_zip.write_bytes(archive.read_bytes())
        target_meta.write_bytes(metadata.read_bytes())
        target_attestation.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--role", choices=("latest", "best"), default="latest")
    parser.add_argument("--destination", type=Path, default=Path("checkpoints"))
    parser.add_argument("--probe-inference", action="store_true")
    args = parser.parse_args()
    print(json.dumps(restore_registered(
        args.registry, args.destination, args.role, inference=args.probe_inference
    ), sort_keys=True))


if __name__ == "__main__":
    main()
