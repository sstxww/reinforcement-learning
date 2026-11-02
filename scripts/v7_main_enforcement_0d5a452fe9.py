#!/usr/bin/env python3
"""Read-only V7 audit: do not confuse a cooperative Actions mutex with main protection.

This deliberately cannot certify globally exclusive merge authority. It gives
an auditable negative verdict when unprotected main allows out-of-band writers.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def assess(branch: dict, rulesets: list) -> dict:
    """Return an evidence classification, never a merge authorization."""
    if not isinstance(branch, dict) or not isinstance(rulesets, list):
        raise ValueError("Malformed GitHub branch/ruleset response")
    if branch.get("name") != "main" or not isinstance(branch.get("commit"), dict):
        raise ValueError("Expected exact main branch identity")
    sha = branch["commit"].get("sha")
    if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("Missing immutable main SHA")
    active = [r.get("id") for r in rulesets if isinstance(r, dict) and r.get("enforcement") == "active"]
    protected = branch.get("protected")
    if type(protected) is not bool:
        raise ValueError("Unknown branch protection state")
    if not protected and not active:
        verdict = "BLOCKED_UNPROTECTED_MAIN"
        reason = "No branch protection or active ruleset; direct REST merge bypasses Actions concurrency"
    else:
        verdict = "BLOCKED_EXCLUSIVITY_NOT_PROVEN"
        reason = "Protection/ruleset presence is insufficient to prove all merge writers use one serialized entry"
    return {
        "repository_branch": "main",
        "main_sha": sha,
        "branch_protected": protected,
        "active_ruleset_ids": active,
        "verdict": verdict,
        "globally_exclusive_merge_permission": False,
        "reason": reason,
    }


def github_get(repository: str, token: str, path: str):
    if not token:
        raise RuntimeError("GitHub token required for read-only live audit")
    req = Request(
        f"https://api.github.com/repos/{repository}{path}",
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "autotavern-main-enforcement-audit",
        },
    )
    with urlopen(req, timeout=15) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only V7 main merge-enforcement audit")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()
    if args.repository != "sstxww/reinforcement-learning":
        print("BLOCKED: unexpected repository", file=sys.stderr)
        return 3
    try:
        token = os.environ.get("GITHUB_TOKEN", "")
        branch = github_get(args.repository, token, "/branches/main")
        rulesets = github_get(args.repository, token, "/rulesets?includes_parents=true")
        record = assess(branch, rulesets)
    except (HTTPError, URLError, ValueError, KeyError, RuntimeError) as exc:
        record = {"verdict": "BLOCKED_UNKNOWN", "globally_exclusive_merge_permission": False,
                  "error_kind": type(exc).__name__}
    output = json.dumps(record, indent=2, sort_keys=True) + "\n"
    print(output, end="")
    if args.json_out:
        from pathlib import Path
        path = Path(args.json_out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
    return 2 if record["verdict"].startswith("BLOCKED") else 0


if __name__ == "__main__":
    sys.exit(main())
