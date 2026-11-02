"""Read-only drift audit: public GitHub Releases versus canonical model registry.

An asset name or API digest is NOT proof of byte download, deserialization,
optimizer state continuation, a complete unassisted game, or model strength.
This tool never writes the registry or grants Champion/Latest status.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from urllib.request import Request, urlopen

REPO = "sstxww/reinforcement-learning"
API = f"https://api.github.com/repos/{REPO}/releases"
TAG = re.compile(r"^[a-zA-Z0-9._-]+$")


def _github_json(url: str) -> object:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "AutoTavern-V5-readonly-audit"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=25) as response:
        return json.load(response)


def collect_releases(fetch=_github_json, max_pages: int = 10) -> list[dict]:
    """Fetch ALL pages or fail, rather than quietly call a partial set complete."""
    if type(max_pages) is not int or not 1 <= max_pages <= 10:
        raise ValueError("max_pages must be 1..10")
    all_rows = []
    seen_ids = set()
    for page in range(1, max_pages + 1):
        rows = fetch(f"{API}?per_page=100&page={page}")
        if not isinstance(rows, list) or len(rows) > 100:
            raise ValueError("Invalid GitHub Releases API page")
        for item in rows:
            if not isinstance(item, dict) or type(item.get("id")) is not int:
                raise ValueError("Malformed GitHub Release record")
            if item["id"] in seen_ids:
                raise ValueError("Duplicate GitHub Release ID across pages")
            seen_ids.add(item["id"])
            all_rows.append(item)
        if len(rows) < 100:
            return all_rows
    raise RuntimeError("Release pagination limit reached; inventory incomplete")


def audit(registry: dict, releases: list[dict]) -> dict:
    """Classify remote Release tags, never infer certified model provenance."""
    if registry.get("schema") != 1 or registry.get("repository") != REPO:
        raise ValueError("Unexpected canonical model registry")
    candidates = registry.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("Missing canonical candidates")
    known = set()
    for c in candidates:
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not TAG.fullmatch(c["id"]):
            raise ValueError("Invalid registered candidate")
        if c["id"] in known:
            raise ValueError("Duplicate registered candidate")
        known.add(c["id"])
    latest = registry.get("latest")
    if not isinstance(latest, dict) or latest.get("id") not in known:
        raise ValueError("Latest is not a registered candidate")
    # Do not trust this audit to validate any pre-existing Champion declaration.
    rows, published_tags = [], set()
    for r in releases:
        if not isinstance(r, dict) or r.get("draft") is not False:
            continue
        tag = r.get("tag_name")
        if not isinstance(tag, str) or not TAG.fullmatch(tag):
            raise ValueError("Invalid published Release tag")
        if tag in published_tags:
            raise ValueError("Duplicate published Release tag")
        published_tags.add(tag)
        assets = r.get("assets")
        if not isinstance(assets, list):
            raise ValueError("Missing Release asset list")
        names = []
        for asset in assets:
            if not isinstance(asset, dict) or not isinstance(asset.get("name"), str):
                raise ValueError("Malformed Release asset")
            names.append(asset["name"])
        if len(names) != len(set(names)):
            raise ValueError("Duplicate asset filenames in Release")
        weight_assets = sorted(n for n in names if n.endswith(".zip"))
        metadata_assets = sorted(n for n in names if n.endswith(".metadata.json"))
        rows.append({
            "tag": tag,
            "published_at": r.get("published_at"),
            "registered": tag in known,
            "zip_assets": weight_assets,
            "metadata_assets": metadata_assets,
            "has_weight_and_metadata_names": bool(weight_assets and metadata_assets),
            "bytes_verified_by_this_audit": False,
            "optimizer_resume_verified_by_this_audit": False,
            "complete_raw_match_verified_by_this_audit": False,
            "promotion_eligible_by_this_audit": False,
        })
    return {
        "schema": 1, "repository": REPO,
        "release_count_published": len(rows),
        "registered_candidate_count": len(known),
        "registered_missing_from_remote_releases": sorted(known - published_tags),
        "unregistered_releases_with_weight_and_metadata_names": sorted(
            r["tag"] for r in rows if not r["registered"] and r["has_weight_and_metadata_names"]
        ),
        "registered_latest": latest["id"],
        "registered_latest_public_release_exists": latest["id"] in published_tags,
        "champion_promotion_performed": False,
        "registry_mutated": False,
        "release_rows": rows,
        "caution": ("This is a metadata-only Release discovery report; an unregistered "
                    "Release must not be resumed, promoted, or called Latest without "
                    "trusted SHA256, byte-download, engine/optimizer, inference, "
                    "true-game and independent evaluation gates."),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    result = audit(registry, collect_releases())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "release_rows"}, sort_keys=True))


if __name__ == "__main__":
    main()
