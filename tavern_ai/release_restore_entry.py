"""Restore a registered, unpromoted GitHub Release without silent reinitialization.

This is a transport/orchestration wrapper around the existing canonical registry,
asset-digest verifier and SB3 checkpoint preflight. It does not promote models,
train, or imply a checkpoint has ever won a real match.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

from .checkpoint_preflight import audit_archive
from .release_asset_verifier import validate_asset_index, verify_local

REPOSITORY = "sstxww/reinforcement-learning"


def choose_model(registry: dict, index: dict, requested: str = "latest") -> dict:
    """Fail closed on unknown or unregistered Release; latest is NOT Champion."""
    validate_asset_index(index, registry)
    model_id = registry["latest"]["id"] if requested == "latest" else requested
    matches = [item for item in registry["candidates"] if item["id"] == model_id]
    if len(matches) != 1 or matches[0]["role"] != "candidate_unpromoted":
        raise ValueError("Not an indexed, unpromoted model: " + model_id)
    return matches[0]



def _install_verified_pair(weights: Path, metadata: Path,
                           target_model: Path, target_meta: Path) -> None:
    """Install verified files without ever clobbering an existing checkpoint.

    Staged files live on the target filesystem. Hard-link creation is exclusive:
    two concurrent restorers cannot both claim the same destination. If the
    second link fails, remove only the first link created by this call. A
    process crash between links can still leave an orphan; subsequent restores
    fail closed rather than silently replacing it.
    """
    installed: list[tuple[Path, Path]] = []
    try:
        for source, destination in ((weights, target_model), (metadata, target_meta)):
            os.link(source, destination)
            installed.append((source, destination))
    except BaseException:
        for source, destination in reversed(installed):
            try:
                # Do not unlink a path that another process replaced meanwhile.
                if destination.samefile(source):
                    destination.unlink()
            except OSError:
                pass
        raise


def restore(registry_path: Path, index_path: Path, output_dir: Path,
            requested: str = "latest", check_load: bool = True) -> dict:
    """Download both versioned Release assets and check them before installing."""
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = choose_model(registry, index, requested)
    model_id = entry["id"]
    if not os.getenv("GH_TOKEN"):
        raise RuntimeError("GH_TOKEN is required for authenticated Release download")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    target_model = output_dir / "model.zip"
    target_meta = output_dir / "model.metadata.json"
    if target_model.exists() or target_meta.exists():
        raise FileExistsError("Refusing to overwrite an existing checkpoint")
    with tempfile.TemporaryDirectory(prefix="release-restore-",
                                     dir=str(output_dir.parent)) as tmp:
        temp = Path(tmp)
        subprocess.run(
            ["gh", "release", "download", model_id, "--repo", REPOSITORY,
             "--pattern", "model.zip", "--pattern", "model.metadata.json",
             "--dir", str(temp)],
            check=True, capture_output=True, text=True)
        weights, metadata = temp / "model.zip", temp / "model.metadata.json"
        verify_local(index, registry, model_id, weights, metadata,
                     check_load=check_load)
        audited = audit_archive(weights, metadata, entry["checkpoint_sha256"])
        if audited["total_timesteps"] != entry["training_steps"]:
            raise ValueError("Registered checkpoint timestep mismatch")
        # Both checks finish before either file is moved into the training path.
        _install_verified_pair(weights, metadata, target_model, target_meta)
    return {"model_id": model_id, "release": entry["release_url"],
            "expected_sha256": entry["checkpoint_sha256"],
            "total_timesteps": entry["training_steps"],
            "weights_and_metadata_hash_verified": True,
            "cpu_load_verified": bool(check_load),
            "optimizer_continuation_performed": False,
            "champion_promoted": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path,
                        default=Path("models/registry.json"))
    parser.add_argument("--asset-index", type=Path,
                        default=Path("models/release_asset_digests.json"))
    parser.add_argument("--model-id", default="latest")
    parser.add_argument("--out-dir", type=Path, default=Path("checkpoints"))
    parser.add_argument("--skip-load", action="store_true",
                        help="Offline digest-only preflight, not a load certification")
    args = parser.parse_args()
    result = restore(args.registry, args.asset_index, args.out_dir,
                     args.model_id, not args.skip_load)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
