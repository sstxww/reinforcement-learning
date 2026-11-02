"""Fail-closed checkpoint source selection for the shared V5 training workflow.

An expiring successful-run Artifact may resume only with a stored checksum;
otherwise use the canonical immutable Release assets. Never turn missing
training history into an unannounced random reinitialization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from .checkpoint_preflight import audit_archive, probe_inference
from .release_asset_verifier import validate_asset_index, verify_local

_TAG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _read(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("Expected a JSON object")
    return document


def release_target(registry: Path, asset_index: Path) -> tuple[str, str]:
    """Resolve exact latest *unpromoted* model and digest, not Champion."""
    canonical, assets = _read(registry), _read(asset_index)
    validate_asset_index(assets, canonical)
    latest = canonical["latest"]
    tag = latest["id"]
    if not isinstance(tag, str) or not _TAG.fullmatch(tag):
        raise ValueError("Unsafe Release tag")
    if latest.get("release_tag") != tag or latest.get("promoted_to_best") is not False:
        raise ValueError("Invalid latest release provenance")
    record = next((x for x in assets["assets"] if x["id"] == tag), None)
    if record is None:
        raise ValueError("Latest candidate absent from asset index")
    if record["weights"]["sha256"] != latest["checkpoint_sha256"]:
        raise ValueError("Latest checkpoint digest disagrees with asset index")
    return tag, record["weights"]["sha256"]


def verify_source(origin: str, weights: Path, metadata: Path, registry: Path,
                  asset_index: Path, *, inference: bool = False) -> dict:
    """Verify bytes before loading. Artifact provenance remains short-lived."""
    if origin not in {"artifact", "release"}:
        raise ValueError("Unknown resume origin")
    if not weights.is_file() or not metadata.is_file():
        raise FileNotFoundError("Both checkpoint and metadata are required")
    if origin == "release":
        model_id, expected = release_target(registry, asset_index)
        index = _read(asset_index)
        canonical = _read(registry)
        verify_local(index, canonical, model_id, weights, metadata)
    else:
        stored = _read(metadata).get("checkpoint_sha256")
        if not isinstance(stored, str) or not re.fullmatch("[a-f0-9]{64}", stored):
            raise ValueError("Artifact lacks trustworthy recorded checkpoint digest")
        expected = stored
        model_id = None
    checked = audit_archive(weights, metadata, expected)
    if inference:
        probe_inference(weights)
    return {
        "source": origin,
        "model_id": model_id,
        "sha256": checked["sha256"],
        "training_steps": checked["total_timesteps"],
        "zip_and_engine_preflight": True,
        "inference_probed": inference,
        "optimizer_continuation_tested": False,
        "champion_promoted": False,
        "durable_source": origin == "release",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--asset-index", type=Path, default=Path("models/release_asset_digests.json"))
    parser.add_argument("--print-release-tag", action="store_true")
    parser.add_argument("--origin", choices=("artifact", "release"))
    parser.add_argument("--weights", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--probe-inference", action="store_true")
    args = parser.parse_args()
    if args.print_release_tag:
        if args.origin or args.weights or args.metadata or args.probe_inference:
            parser.error("Release-tag lookup cannot verify local files")
        print(release_target(args.registry, args.asset_index)[0])
        return
    if not all((args.origin, args.weights, args.metadata)):
        parser.error("--origin, --weights and --metadata are required together")
    report = verify_source(args.origin, args.weights, args.metadata, args.registry,
                           args.asset_index, inference=args.probe_inference)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
