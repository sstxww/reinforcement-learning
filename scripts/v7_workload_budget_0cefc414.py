#!/usr/bin/env python3
"""Read-only advisory Actions capacity preflight; never a reservation or merge lock."""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# GitHub "action_required" is a workflow CONCLUSION filter, not an active run status.
# Including it would count completed runs and make an advisory permanently fail.
ACTIVE = ("queued", "in_progress", "waiting", "requested", "pending")
HEAVY = re.compile(r"(?:^|[\s_/-])(?:train(?:ing)?|ppo|resume|continuation|self[-_ ]?play)(?:$|[\s_/-])", re.I)

class BudgetError(RuntimeError):
    pass

def summarize(pages, own_run_id=None):
    """Validate complete status-scoped pages and deduplicate GitHub run IDs."""
    if set(pages) != set(ACTIVE):
        raise BudgetError("Incomplete active-status coverage")
    seen = {}
    for status, page in pages.items():
        if not isinstance(page, dict) or not isinstance(page.get("workflow_runs"), list):
            raise BudgetError("Missing workflow_runs page")
        runs = page["workflow_runs"]
        count = page.get("total_count")
        if isinstance(count, bool) or not isinstance(count, int) or count != len(runs):
            raise BudgetError("API pagination incomplete or total_count invalid")
        for run in runs:
            if not isinstance(run, dict) or run.get("status") != status:
                raise BudgetError("Status-filtered run mismatch")
            run_id = run.get("id")
            if isinstance(run_id, bool) or not isinstance(run_id, int) or run_id < 1:
                raise BudgetError("Missing stable run identity")
            if run_id == own_run_id:
                continue
            if run_id in seen and seen[run_id] != run:
                raise BudgetError("Conflicting duplicate run identity")
            seen[run_id] = run
    heavy = [r for r in seen.values() if HEAVY.search(str(r.get("name") or ""))]
    return {"active_total": len(seen), "named_training_total": len(heavy),
            "active_run_ids": sorted(seen), "training_run_ids": sorted(r["id"] for r in heavy),
            "scope": "advisory_snapshot_not_atomic"}

def preflight(snapshot, max_active, max_training):
    if max_active < 1 or max_training < 1:
        raise BudgetError("Limits must be positive")
    if snapshot["active_total"] >= max_active or snapshot["named_training_total"] >= max_training:
        raise BudgetError("Capacity threshold reached; avoid starting a new bounded run")
    return snapshot

def github_pages(repo, token):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo or "") or not token:
        raise BudgetError("GITHUB_REPOSITORY/GITHUB_TOKEN required")
    pages = {}
    for status in ACTIVE:
        url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=100&status={status}"
        req = Request(url, headers={"Authorization": f"Bearer {token}",
                                    "Accept": "application/vnd.github+json",
                                    "X-GitHub-Api-Version": "2022-11-28",
                                    "User-Agent": "autotavern-read-only-budget-preflight"})
        try:
            with urlopen(req, timeout=15) as response:
                pages[status] = json.load(response)
        except (HTTPError, URLError, ValueError) as exc:
            raise BudgetError(f"Actions status {status} unavailable: {type(exc).__name__}") from exc
    return pages

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-active", type=int, default=20)
    parser.add_argument("--max-training", type=int, default=4)
    args = parser.parse_args()
    own = os.environ.get("GITHUB_RUN_ID", "")
    own_id = int(own) if own.isdigit() else None
    result = preflight(summarize(github_pages(os.environ.get("GITHUB_REPOSITORY"),
                                               os.environ.get("GITHUB_TOKEN")), own_id),
                       args.max_active, args.max_training)
    print(json.dumps(result, sort_keys=True))
    print("ADVISORY ONLY: not an atomic budget claim, lock, or proof of exclusive merge ownership")

if __name__ == "__main__":
    try:
        main()
    except BudgetError as exc:
        print("V7_BUDGET_BLOCKED: " + str(exc), file=sys.stderr)
        sys.exit(1)
