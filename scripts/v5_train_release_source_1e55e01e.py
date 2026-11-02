"""Select a *registered* durable Release checkpoint for a bounded main continuation.

This is a source-selection gate, not proof that the published bytes load,
resume, win, or even exist; the workflow must download and verify them.
Fail closed rather than silently initializing new PPO weights.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from tavern_ai.registry_integrity import validate_registry

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_PREFIX = "https://github.com/sstxww/reinforcement-learning/releases/tag/"


def select_source(registry: dict, requested: str | None = None) -> dict:
    validate_registry(registry)
    latest = registry["latest"]
    chosen_id = requested or latest["id"]
    model = next((m for m in registry["candidates"] if m["id"] == chosen_id), None)
    if model is None:
        raise ValueError("Unregistered checkpoint: refusing to train")
    if model["role"] != "candidate_unpromoted":
        raise ValueError("Only explicit unpromoted candidates may be source checkpoints")
    if model.get("release_url") != _PREFIX + chosen_id:
        raise ValueError("Release tag or repository mismatch")
    digest = model.get("checkpoint_sha256")
    if not isinstance(digest, str) or _SHA.fullmatch(digest) is None:
        raise ValueError("Invalid expected checkpoint SHA256")
    if type(model.get("training_steps")) is not int or model["training_steps"] <= 0:
        raise ValueError("Unknown cumulative training steps")
    # A model registry records *claims*. The actual published ZIP, metadata,
    # source compatibility and optimizer have to be checked after download.
    return {
        "model_id": chosen_id,
        "release_tag": chosen_id,
        "expected_sha256": digest,
        "expected_steps": model["training_steps"],
        "source_is_verified_for_resume": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--model-id", default=None)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    result = select_source(json.loads(args.registry.read_text(encoding="utf-8")), args.model_id)
    # github-output is a fixed path supplied by runner, not interpreted as shell.
    if args.github_output is not None:
        with args.github_output.open("a", encoding="utf-8") as output:
            for key in ("model_id", "release_tag", "expected_sha256", "expected_steps"):
                print(f"{key}={result[key]}", file=output)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
