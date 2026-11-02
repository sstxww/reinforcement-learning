"""Read-only, fail-closed V7 PR head audit; NOT a merge authorization.

The verified latest HEAD and main commit are caller supplied to prevent a stale
snapshot from being accidentally described as ready. A positive audit only
means that *preliminary* mechanical checks passed: independent review, receipts,
merge-base validation, exclusivity lease and branch rules remain mandatory.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
REPO_PATTERN = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def assess(pr: dict, branch: dict, checks: list[dict], expected_head: str, expected_main: str) -> dict:
    """Pure gate function: never labels a PR ready for immediate merge."""
    reasons: list[str] = []
    if pr.get("state") != "open":
        reasons.append("pr_not_open")
    if pr.get("draft") is not False:
        reasons.append("pr_draft_or_unknown")
    if (pr.get("base") or {}).get("ref") != "main":
        reasons.append("wrong_target_branch")
    if (pr.get("head") or {}).get("sha") != expected_head:
        reasons.append("head_sha_changed")
    if ((branch.get("commit") or {}).get("sha")) != expected_main:
        reasons.append("main_sha_changed")
    if (pr.get("base") or {}).get("sha") != expected_main:
        reasons.append("pr_base_not_current_main")
    if pr.get("mergeable") is not True:
        reasons.append("mergeability_not_verified")
    if pr.get("mergeable_state") in ("dirty", "blocked", "unknown", "unstable"):
        reasons.append("mergeable_state_not_clean")

    ci_ok = any(
        check.get("head_sha") == expected_head
        and check.get("status") == "completed"
        and check.get("conclusion") == "success"
        and (check.get("name") == "tests-and-full-match")
        and (check.get("app") or {}).get("slug") == "github-actions"
        for check in checks
    )
    if not ci_ok:
        reasons.append("no_successful_exact_head_full_match_check")
    return {
        "schema": 1,
        "pr_number": pr.get("number"),
        "checked_main_sha": expected_main,
        "checked_pr_head_sha": expected_head,
        "preliminary_status": "blocked" if reasons else "needs_integrator_review",
        "blockers": reasons,
        "not_checked": [
            "exclusive_integration_lease", "required_code_review", "branch_protection",
            "authentic_eight_seat_receipts_and_identity", "model_digest_and_optimizer",
            "current_combined_main_and_pr_test", "secrets_and_overlap_review",
        ],
        "merge_authorized": False,
    }


def api_get(path: str, token: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "AutoTavern-V7-ReadOnly-Audit",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def run(repo: str, number: int, head: str, main: str, token: str = "") -> dict:
    if not REPO_PATTERN.fullmatch(repo) or not SHA_PATTERN.fullmatch(head) or not SHA_PATTERN.fullmatch(main):
        raise ValueError("Require repository owner/name and two exact 40-character commit SHAs")
    if number < 1:
        raise ValueError("PR number must be positive")
    prefix = f"/repos/{repo}"
    pr = api_get(f"{prefix}/pulls/{number}", token)
    branch = api_get(f"{prefix}/branches/main", token)
    checks_result = api_get(f"{prefix}/commits/{head}/check-runs?per_page=100", token)
    if checks_result.get("total_count", 0) > len(checks_result.get("check_runs", [])):
        return {
            "schema": 1, "pr_number": number, "checked_main_sha": main,
            "checked_pr_head_sha": head, "preliminary_status": "blocked",
            "blockers": ["check_runs_paginated_or_incomplete"],
            "merge_authorized": False,
        }
    return assess(pr, branch, checks_result.get("check_runs", []), head, main)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="sstxww/reinforcement-learning")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--expected-head-sha", required=True)
    parser.add_argument("--expected-main-sha", required=True)
    args = parser.parse_args()
    try:
        result = run(args.repo, args.pr, args.expected_head_sha,
                     args.expected_main_sha, os.getenv("GITHUB_TOKEN", ""))
    except (ValueError, urllib.error.URLError, TimeoutError):
        print(json.dumps({"preliminary_status": "blocked", "reason": "api_or_input_error",
                          "merge_authorized": False}))
        sys.exit(2)
    print(json.dumps(result, sort_keys=True, indent=2))
    if result["preliminary_status"] == "blocked":
        sys.exit(1)


if __name__ == "__main__":
    main()
