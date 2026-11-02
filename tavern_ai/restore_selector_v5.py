"""Select one independently cataloged, durable, UNPROMOTED PPO Release for main training.

No API calls or mutable 'latest' tags. A failing gate MUST abort the workflow:
silently starting from random weights breaks continual training lineage.
This is a selection/byte-integrity prerequisite, not a performance certificate.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES

REPOSITORY = "sstxww/reinforcement-learning"
RELEASE_ROOT = f"https://github.com/{REPOSITORY}/releases/tag/"
TAG_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")


def select_release(registry: dict) -> dict:
    if not isinstance(registry, dict) or registry.get("schema") != 1:
        raise ValueError("Unrecognized model registry schema")
    if registry.get("repository") != REPOSITORY:
        raise ValueError("Unexpected model registry repository")
    env = registry.get("engine")
    expected = {
        "version": "1.1.0", "source_hash": ENGINE_HASH,
        "float_features": FEATURES, "card_slots": CARDS,
        "action_count": ACTIONS,
    }
    if not isinstance(env, dict) or any(env.get(k) != v for k, v in expected.items()):
        raise ValueError("Registry engine/observation/action contract mismatch")

    latest = registry.get("latest")
    if not isinstance(latest, dict):
        raise ValueError("No registered durable continuation source")
    tag, model_id = latest.get("release_tag"), latest.get("id")
    if not isinstance(tag, str) or not TAG_RE.fullmatch(tag) or tag != model_id:
        raise ValueError("Untrusted Release tag or model identifier")
    if latest.get("durable_storage") != "github_release":
        raise ValueError("Latest checkpoint is not durable")
    if latest.get("release") != RELEASE_ROOT + tag:
        raise ValueError("Release URL does not match immutable tag")
    if (latest.get("model_asset"), latest.get("metadata_asset")) != (
        "model.zip", "model.metadata.json"
    ):
        raise ValueError("Unexpected Release asset names")
    digest = latest.get("checkpoint_sha256")
    steps = latest.get("training_steps")
    if not isinstance(digest, str) or not SHA_RE.fullmatch(digest):
        raise ValueError("Invalid trusted model SHA256")
    if type(steps) is not int or steps < 128:
        raise ValueError("Invalid prior model training step count")
    for flag in ("release_download_sha256_verified", "model_load_verified",
                 "real_resume_128_steps_verified", "model_full_game_passed"):
        if latest.get(flag) is not True:
            raise ValueError(f"Unverified continuation gate: {flag}")

    # A role pointer alone is insufficient: a second catalog record must agree.
    records = registry.get("candidates")
    if not isinstance(records, list):
        raise ValueError("Missing immutable candidate catalog")
    matches = [row for row in records
               if isinstance(row, dict) and row.get("id") == model_id]
    if len(matches) != 1:
        raise ValueError("Missing or duplicated source candidate")
    row = matches[0]
    if (row.get("checkpoint_sha256") != digest or
            row.get("training_steps") != steps or
            row.get("release_url") != RELEASE_ROOT + tag):
        raise ValueError("Canonical candidate disagrees with latest pointer")
    return {"tag": tag, "sha256": digest, "steps": steps, "role": "unpromoted_continuation_source"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    selected = select_release(json.loads(args.registry.read_text(encoding="utf-8")))
    if args.github_output is not None:
        with args.github_output.open("a", encoding="utf-8") as stream:
            for name in ("tag", "sha256", "steps"):
                stream.write(f"{name}={selected[name]}\n")
    print(json.dumps(selected, sort_keys=True))


if __name__ == "__main__":
    main()
