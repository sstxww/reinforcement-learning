"""Read-only strict PR head/run/job audit; never grants a main merge lease.

Successful PR HEAD checks are necessary, not sufficient, for merging. This tool
cannot attest to the tested merge commit, manual review or exclusive integration.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

_REQUIRED_STEPS = {
    "Unit tests and PR evidence",
    "Install pinned engine and verified patch",
    "Confirm engine layout",
    "Real full eight-seat simulated match",
    "Preserve CI evidence",
}


def validate(repo: str, pr: dict, main_sha: str, expected_head: str,
             runs: list[dict], jobs: dict | None) -> dict:
    """Fail closed on drift, wrong CI identity, zero jobs and skipped game steps."""
    failures: list[str] = []
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Invalid repository selector")
    if not re.fullmatch(r"[0-9a-f]{40}", expected_head):
        raise ValueError("Expected full 40-character head SHA")
    if not re.fullmatch(r"[0-9a-f]{40}", main_sha):
        raise ValueError("Invalid main SHA")
    if pr.get("draft") or pr.get("state") != "open":
        failures.append("PR is not an open, ready-for-review change")
    if pr.get("head", {}).get("sha") != expected_head:
        failures.append("Expected PR head SHA is stale")
    if pr.get("base", {}).get("ref") != "main":
        failures.append("PR does not target main")
    if pr.get("base", {}).get("sha") != main_sha:
        failures.append("Current main differs from the PR base SHA")
    if pr.get("mergeable_state") != "clean":
        failures.append("GitHub mergeability is not clean")

    matching = [r for r in runs if r.get("head_sha") == expected_head
                and r.get("event") == "pull_request"
                and r.get("name") == "CI - full-match gate"]
    latest = max(matching, key=lambda r: (r.get("created_at") or "", r.get("id") or 0), default=None)
    if latest is None:
        failures.append("No exact-head PR full-match CI workflow found")
    elif latest.get("status") != "completed" or latest.get("conclusion") != "success":
        failures.append("Latest exact-head CI did not complete successfully")

    # GitHub may report an action_required workflow with 0 jobs; it is never a pass.
    if latest is not None and latest.get("status") == "completed" and latest.get("conclusion") == "success":
        raw_jobs = jobs.get("jobs", []) if isinstance(jobs, dict) else []
        if not raw_jobs or jobs.get("total_count") != len(raw_jobs):
            failures.append("CI jobs missing or job pagination incomplete")
        else:
            full = [j for j in raw_jobs if j.get("name") == "tests-and-full-match"]
            if len(full) != 1 or full[0].get("conclusion") != "success":
                failures.append("No successful full-match CI job")
            else:
                passed = {s.get("name") for s in full[0].get("steps", [])
                          if s.get("status") == "completed" and s.get("conclusion") == "success"}
                missing = _REQUIRED_STEPS - passed
                if missing:
                    failures.append("Unverified CI steps: " + ", ".join(sorted(missing)))
    return {
        "schema": 1, "repository": repo, "pr_number": pr.get("number"),
        "expected_head_sha": expected_head, "main_sha": main_sha,
        "run_id": latest.get("id") if latest else None,
        "run_url": latest.get("html_url") if latest else None,
        "ci_preflight_passed": not failures,
        "merge_authorized": False,
        "reason": "Read-only job/step evidence cannot prove exclusive integration, required reviews, or tested merge tree",
        "blockers": failures,
    }


def api_get(repo: str, suffix: str) -> dict:
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "autotavern-v7-head-ci-audit",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(f"https://api.github.com/repos/{repo}/{suffix}", headers=headers)
    try:
        with urlopen(request, timeout=25) as resp:
            return json.load(resp)
    except HTTPError as err:
        raise RuntimeError(f"GitHub API failed with HTTP {err.code} on {suffix.split('?')[0]}") from err


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="sstxww/reinforcement-learning")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        parser.error("invalid repo name")
    if args.pr < 1:
        parser.error("invalid PR number")
    pr = api_get(args.repo, f"pulls/{args.pr}")
    main_sha = api_get(args.repo, "branches/main")["commit"]["sha"]
    run_data = api_get(args.repo, f"actions/runs?head_sha={quote(args.expected_head)}&event=pull_request&per_page=100")
    matching = [r for r in run_data.get("workflow_runs", []) if r.get("head_sha") == args.expected_head
                and r.get("event") == "pull_request" and r.get("name") == "CI - full-match gate"]
    latest = max(matching, key=lambda r: (r.get("created_at") or "", r.get("id") or 0), default=None)
    jobs = api_get(args.repo, f"actions/runs/{latest['id']}/jobs?per_page=100") if latest else None
    result = validate(args.repo, pr, main_sha, args.expected_head, run_data.get("workflow_runs", []), jobs)
    # Detect a main move while querying jobs; the snapshot must not be accepted.
    if api_get(args.repo, "branches/main")["commit"]["sha"] != main_sha:
        result["blockers"].append("Main SHA moved during audit")
        result["ci_preflight_passed"] = False
    body = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        from pathlib import Path
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    print(body)
    if not result["ci_preflight_passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
