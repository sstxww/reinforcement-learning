"""Fail-closed Release checkpoint attestation; no Champion promotion.

This module is intentionally standalone, with no changes to shared trainer code.
It verifies an immutable source Release before PPO.load and writes compatible
metadata for an independently continued checkpoint after real training.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import zipfile
from pathlib import Path

ENGINE_HASH = "6d8712c93022ba11"
RELEASE_TAG = "v2-learning-41413557445"
RELEASE_SHA256 = "73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a"
RELEASE_STEPS = 1280


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("Checkpoint metadata must be a JSON object")
    return obj


def check_zip(path: Path) -> None:
    if not path.is_file() or path.stat().st_size < 100:
        raise ValueError("Missing/empty model checkpoint")
    try:
        with zipfile.ZipFile(path) as f:
            if not f.namelist() or f.testzip() is not None:
                raise ValueError("Damaged checkpoint archive")
    except zipfile.BadZipFile as exc:
        raise ValueError("Damaged checkpoint archive") from exc


def check_source(model: Path, metadata: Path,
                 expected_hash: str = RELEASE_SHA256,
                 expected_steps: int = RELEASE_STEPS) -> dict:
    check_zip(model)
    m = load_json(metadata)
    actual = digest(model)
    if actual != expected_hash or m.get("checkpoint_sha256") != expected_hash:
        raise ValueError("Release SHA256 mismatch: unsafe to deserialize")
    if type(m.get("total_timesteps")) is not int or m["total_timesteps"] != expected_steps:
        raise ValueError("Unexpected source cumulative PPO steps")
    engine = m.get("engine")
    if not isinstance(engine, dict) or engine.get("version") != "1.1.0" or engine.get("source_hash") != ENGINE_HASH:
        raise ValueError("TavernGym engine fingerprint mismatch")
    compatibility = m.get("compatibility")
    if not isinstance(compatibility, dict) or compatibility.get("engine") != engine:
        raise ValueError("Missing/mismatched catalog and engine compatibility metadata")
    if not all(compatibility.get(k) for k in ("catalog_sha256", "ruleset_id", "patch_sha256", "upstream_commit")):
        raise ValueError("Incomplete checkpoint provenance")
    if m.get("algorithm") != "MaskablePPO":
        raise ValueError("Unexpected checkpoint algorithm")
    return m


def attest_resumed(source_model: Path, source_metadata: Path, resumed_model: Path,
                   resumed_metadata: Path, output: Path, delta: int = 128,
                   expected_hash: str = RELEASE_SHA256,
                   expected_steps: int = RELEASE_STEPS) -> dict:
    parent = check_source(source_model, source_metadata, expected_hash, expected_steps)
    check_zip(resumed_model)
    new = load_json(resumed_metadata)
    if type(delta) is not int or delta < 128:
        raise ValueError("Invalid intended continuation length")
    if type(new.get("total_timesteps")) is not int or new["total_timesteps"] != expected_steps + delta:
        raise ValueError("PPO did not continue for exactly the required number of steps")
    if new.get("engine") != parent["engine"] or new.get("algorithm") != parent["algorithm"]:
        raise ValueError("Resumed checkpoint incompatible with source")
    if digest(resumed_model) == expected_hash:
        raise ValueError("Continuation produced unchanged checkpoint bytes")
    # Current main trainer creates schema-1 metadata. Add the verified
    # schema-2 provenance required by the existing learning PR's recovery code.
    new.update({
        "schema": 2,
        "compatibility": parent["compatibility"],
        "checkpoint_sha256": digest(resumed_model),
        "increment_timesteps": delta,
        "parent_release_tag": RELEASE_TAG,
        "parent_checkpoint_sha256": expected_hash,
        "role": "challenger_unpromoted",
    })
    temp = resumed_metadata.with_name(resumed_metadata.name + ".tmp")
    temp.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, resumed_metadata)
    report = {
        "schema": 1,
        "source_release": RELEASE_TAG,
        "source_checkpoint_sha256": expected_hash,
        "source_total_timesteps": expected_steps,
        "resumed_checkpoint_sha256": new["checkpoint_sha256"],
        "resumed_total_timesteps": new["total_timesteps"],
        "increment_timesteps": delta,
        "engine": new["engine"],
        "model_role": "challenger_unpromoted",
        "promotion": "none",
        "complete_game_verified": False,
        "warning": "Hash and PPO step verification only; full-game and paired evaluation are separate gates.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("preflight", "postflight"))
    p.add_argument("--source-model", type=Path, required=True)
    p.add_argument("--source-metadata", type=Path, required=True)
    p.add_argument("--resumed-model", type=Path)
    p.add_argument("--resumed-metadata", type=Path)
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    if args.phase == "preflight":
        meta = check_source(args.source_model, args.source_metadata)
        print(json.dumps({"source_release": RELEASE_TAG, "verified_sha256": RELEASE_SHA256,
                          "total_timesteps": meta["total_timesteps"], "role": "unpromoted"}))
    else:
        if not all((args.resumed_model, args.resumed_metadata, args.report)):
            p.error("postflight requires resumed model, metadata and report")
        print(json.dumps(attest_resumed(args.source_model, args.source_metadata,
                                        args.resumed_model, args.resumed_metadata,
                                        args.report), ensure_ascii=False))


if __name__ == "__main__":
    main()
