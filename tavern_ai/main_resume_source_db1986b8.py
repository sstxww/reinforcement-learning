"""Select the sole registered durable V5 continuation source; never guess a checkpoint.

This only validates the trusted registry selection. Download, byte/hash verification,
CPU load, genuine PPO continuation and raw full games are separate hard gates.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .registry_integrity import validate_registry

_TAG = re.compile(r"[A-Za-z0-9._-]+\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_RELEASE = "https://github.com/sstxww/reinforcement-learning/releases/tag/"


def select_source(registry: dict) -> dict:
    validate_registry(registry)
    latest = registry["latest"]
    tag = latest["id"]
    matching = [x for x in registry["candidates"] if x["id"] == tag]
    if len(matching) != 1 or not _TAG.fullmatch(tag):
        raise ValueError("Ambiguous or unsafe registered source tag")
    candidate = matching[0]
    sha = latest["checkpoint_sha256"]
    steps = latest["training_steps"]
    if not _SHA.fullmatch(sha) or sha != candidate["checkpoint_sha256"]:
        raise ValueError("Source SHA256 is not the immutable registered value")
    if type(steps) is not int or steps != candidate["training_steps"]:
        raise ValueError("Source step count differs from registered candidate")
    if latest.get("release_tag") != tag or latest.get("release") != _RELEASE + tag:
        raise ValueError("Latest Release tag and URL do not match")
    if latest.get("durable_storage") not in {"github_release", "GitHub Release"}:
        raise ValueError("Temporary Actions artifacts are not durable sources")
    if latest.get("model_asset") != "model.zip" or latest.get("metadata_asset") != "model.metadata.json":
        raise ValueError("Expected immutable model and metadata Release assets")
    if latest.get("model_full_game_passed") is not True:
        raise ValueError("Source has no registered full-model-game completion")
    if latest.get("paired_improvement_verified") is not False:
        raise ValueError("Unreviewed model strength must not be treated as established")
    return {
        "model_tag": tag,
        "expected_sha256": sha,
        "source_steps": steps,
        "role": "unpromoted_research_source",
        "verified": "registry_selection_only",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    p.add_argument("--github-output", type=Path)
    args = p.parse_args()
    selected = select_source(json.loads(args.registry.read_text(encoding="utf-8")))
    if args.github_output is not None:
        with args.github_output.open("a", encoding="utf-8") as f:
            for key in ("model_tag", "expected_sha256", "source_steps"):
                f.write(f"{key}={selected[key]}\n")
    print(json.dumps(selected, sort_keys=True))


if __name__ == "__main__":
    main()
