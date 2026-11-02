"""Fail-closed Release recovery for the existing canonical training pipeline.

This is an opt-in infrastructure gate, NOT model promotion or evidence of strength.
Never falls back to random initialization or a short-lived Actions artifact.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from .checkpoint_preflight import audit_archive, probe_inference
from .registry_integrity import validate_registry
from .release_asset_verifier import validate_asset_index, verify_local

REPOSITORY = "sstxww/reinforcement-learning"


def choose_latest(canonical: dict, asset_index: dict) -> str:
    """Use only the registered unpromoted latest candidate, not newest by timestamp."""
    validate_registry(canonical)
    validate_asset_index(asset_index, canonical)
    latest = canonical["latest"]
    ident = latest["id"]
    if (latest.get("role") != "latest_experimental_unpromoted"
            or latest.get("release_tag") != ident
            or latest.get("model_asset") != "model.zip"
            or latest.get("metadata_asset") != "model.metadata.json"
            or latest.get("promoted_to_best") is not False
            or latest.get("model_full_game_passed") is not True):
        raise ValueError("Latest Release has not passed the checkpoint lineage gate")
    return ident


def _download(tag: str, directory: Path) -> None:
    """Noninteractive GitHub CLI download; caller validates both actual files."""
    subprocess.run([
        "gh", "release", "download", tag, "--repo", REPOSITORY,
        "--pattern", "model.zip", "--pattern", "model.metadata.json",
        "--dir", str(directory),
    ], check=True, timeout=240, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def restore(
    canonical_path: Path,
    asset_index_path: Path,
    output_dir: Path,
    *,
    require_inference: bool = False,
    downloader: Callable[[str, Path], None] = _download,
) -> dict:
    """Verify Release bytes, optimizer ZIP and engine before atomic publish.

    The output directory must not exist. Failures leave it absent; callers must
    not interpret any error as permission to initialize an unrelated model.
    """
    canonical_path, asset_index_path, output_dir = (
        Path(canonical_path), Path(asset_index_path), Path(output_dir))
    if output_dir.exists():
        raise FileExistsError("Refusing to replace any existing checkpoint directory")
    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    index = json.loads(asset_index_path.read_text(encoding="utf-8"))
    tag = choose_latest(canonical, index)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=".release-restore-", dir=output_dir.parent))
    try:
        downloader(tag, scratch)
        weights = scratch / "model.zip"
        metadata = scratch / "model.metadata.json"
        if not weights.is_file() or not metadata.is_file():
            raise FileNotFoundError("Release missing weight or metadata asset; no fallback")
        if weights.is_symlink() or metadata.is_symlink():
            raise ValueError("Refusing symlinked Release assets")
        evidence = verify_local(index, canonical, tag, weights, metadata)
        if evidence["weight_bytes_sha256_verified"] is not True or evidence["metadata_bytes_sha256_verified"] is not True:
            raise ValueError("Both Release asset digests must be verified")
        audit = audit_archive(weights, metadata, canonical["latest"]["checkpoint_sha256"])
        if require_inference:
            probe_inference(weights)
        result = {
            "schema": 1,
            "source": "immutable_registered_github_release",
            "release_tag": tag,
            "sha256": canonical["latest"]["checkpoint_sha256"],
            "training_steps_before_resume": audit["total_timesteps"],
            "sha256_and_metadata_verified": True,
            "optimizer_zip_integrity_verified": audit["archive_integrity"] == "passed",
            "cpu_inference_checked": require_inference,
            "optimizer_continuation_checked": False,
            "competitiveness_checked": False,
            "promoted_to_champion": False,
        }
        (scratch / "restore-attestation.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if output_dir.exists():
            raise FileExistsError("Checkpoint directory appeared during recovery")
        os.rename(scratch, output_dir)
        return result
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--index", type=Path, default=Path("models/release_asset_digests.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("checkpoints"))
    parser.add_argument("--probe-inference", action="store_true")
    args = parser.parse_args()
    print(json.dumps(restore(args.registry, args.index, args.output_dir,
                             require_inference=args.probe_inference), sort_keys=True))


if __name__ == "__main__":
    main()
