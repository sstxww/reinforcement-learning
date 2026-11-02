"""Read-only fail-closed changed-file overlap audit for V6.1 PR triage.

A file overlap is a review FLAG, not proof of merge conflict or merge approval.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

REPO = "sstxww/reinforcement-learning"
MAX_FILES = 500

def _check(pr):
    if not isinstance(pr, dict) or type(pr.get("number")) is not int or pr["number"] < 1:
        raise ValueError("Invalid PR number")
    paths = pr.get("files")
    if not isinstance(paths, list) or len(paths) > MAX_FILES or any(
        not isinstance(p, str) or not p or p.startswith("/") or ".." in p.split("/")
        for p in paths
    ) or len(paths) != len(set(paths)):
        raise ValueError("Missing or untrusted complete changed-file inventory")
    return pr

def audit(target, others):
    target = _check(target)
    seen = {target["number"]}
    overlaps = []
    for other in others:
        other = _check(other)
        if other["number"] in seen:
            raise ValueError("Self/duplicate comparison is invalid")
        seen.add(other["number"])
        shared = sorted(set(target["files"]) & set(other["files"]))
        if shared:
            overlaps.append({
                "pr": other["number"], "draft": other.get("draft"),
                "paths": shared,
                "high_risk": any(
                    p in {".github/workflows/train.yml", "models/registry.json"}
                    or p.startswith("tavern_ai/") for p in shared
                ),
                "review_only": True
            })
    return {
        "schema": 1, "target_pr": target["number"],
        "target_head_sha": target.get("head_sha"),
        "checked_other_prs": len(others),
        "overlaps": sorted(overlaps, key=lambda item: item["pr"]),
        "no_overlap_is_not_merge_approval": True,
        "ci_receipt_release_gate": "not_evaluated"
    }

def _api(url):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Read-only token required; no inferred/stale PR data")
    request = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "autotavern-v61-pr-overlap"
    })
    with urlopen(request, timeout=20) as response:
        return json.load(response)

def github_pr(number):
    base = f"https://api.github.com/repos/{REPO}/pulls/{number}"
    meta = _api(base)
    if not isinstance(meta, dict) or meta.get("number") != number:
        raise ValueError("PR metadata mismatch")
    files = []
    for page in range(1, 7):
        rows = _api(f"{base}/files?per_page=100&page={page}")
        if not isinstance(rows, list):
            raise ValueError("Malformed GitHub changed-file result")
        files.extend(row["filename"] for row in rows)
        if len(files) > MAX_FILES:
            raise ValueError("PR file inventory exceeds review budget")
        if len(rows) < 100:
            break
    else:
        raise ValueError("GitHub file inventory truncated")
    if len(files) != meta.get("changed_files"):
        raise ValueError("GitHub file count disagrees with enumerated list")
    return _check({"number": number, "files": files, "draft": meta.get("draft"),
                   "head_sha": meta.get("head", {}).get("sha")})

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--snapshot", type=Path)
    mode.add_argument("--github-target", type=int)
    parser.add_argument("--against", type=int, nargs="*", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.snapshot:
        data = json.loads(args.snapshot.read_text(encoding="utf-8"))
        target, others = data["target"], data["others"]
    else:
        if args.github_target < 1 or not 1 <= len(args.against) <= 12:
            parser.error("Live mode requires target PR and 1..12 comparators")
        target = github_pr(args.github_target)
        others = [github_pr(p) for p in args.against]
    rendered = json.dumps(audit(target, others), sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")

if __name__ == "__main__":
    main()
