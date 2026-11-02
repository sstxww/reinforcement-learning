"""Read-only V5 PR integration inventory. Never approves or merges PRs automatically.

Uses *current* main, PR head and same-head Actions evidence. A category A entry
is a review queue candidate, NOT permission to merge or a gameplay-strength claim.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

API = "https://api.github.com"
NEGATIVE = (
    "no competitive gain", "no strength gain", "no stable", "no rank gain",
    "negative", "reject", "worse", "no observed gain", "no confirmed gain",
    "transfer failure", "no established rank gain", "no measurable gain",
)


def repo_path(repo: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Expected owner/repo, no API URLs or extra paths")
    return "/repos/" + repo


def api_get(path: str) -> dict | list:
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    req = Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "autotavern-v5-pr-integration-audit",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": "Bearer " + token} if token else {}),
        },
    )
    try:
        with urlopen(req, timeout=30) as response:
            return json.load(response)
    except HTTPError as exc:
        # Avoid logging token or potentially sensitive response headers.
        raise RuntimeError(f"GitHub API failed: HTTP {exc.code} ({path})") from exc


def all_open_prs(base: str) -> list[dict]:
    results = []
    for page in range(1, 11):
        batch = api_get(f"{base}/pulls?state=open&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("Unexpected GitHub PR listing")
        results.extend(batch)
        if len(batch) < 100:
            return results
    raise RuntimeError("PR pagination exceeds safety bound (1000); audit incomplete")


def latest_head_ci(runs: list[dict], head: str) -> dict:
    gates = [
        r for r in runs
        if r.get("head_sha") == head and r.get("name") == "CI - full-match gate"
        and r.get("event") == "pull_request"
    ]
    if not gates:
        return {"state": "missing", "url": None, "run_id": None}
    latest = max(gates, key=lambda r: (r.get("created_at") or "", r.get("id") or 0))
    state = (
        latest.get("conclusion") or "unknown"
        if latest.get("status") == "completed" else "pending"
    )
    return {"state": state, "url": latest.get("html_url"), "run_id": latest.get("id")}


def classify(pr: dict, ci: dict) -> tuple[str, list[str]]:
    title = str(pr.get("title") or "").lower()
    body = str(pr.get("body") or "").lower()
    state = str(pr.get("mergeable_state") or "unknown")
    problems = []
    if pr.get("draft"):
        problems.append("Draft: author/review gates not cleared")
    if pr.get("base", {}).get("ref") != "main":
        problems.append("Stacked dependency: base is not main")
    if state in ("dirty", "blocked"):
        problems.append("Merge conflicts or branch gate: " + state)
    if state in ("unknown", "unstable"):
        problems.append("Mergeability not confirmed: " + state)
    if ci["state"] != "success":
        problems.append("No SUCCESS on exact latest PR HEAD for CI full-match gate: " + ci["state"])
    if state == "dirty":
        return "E_conflict_or_overlap", problems
    if any(term in title for term in NEGATIVE):
        return "D_negative_or_no_gain", problems + ["No verified promotion signal; retain research evidence"]
    if pr.get("base", {}).get("ref") != "main" or pr.get("draft") or ci["state"] != "success":
        return "B_fix_or_verify_before_merge", problems
    if state != "clean":
        return "B_fix_or_verify_before_merge", problems
    if any(x in title + " " + body[:1500] for x in ("ppo", "strategy", "policy", "reward", "rank gain", "challenger")):
        return "C_performance_review_required", problems + ["Separately verify held-out, seat-rotated performance and fallback"]
    return "A_engineering_review_candidate", problems + [
        "Manual diff, dependencies, receipts, security and main HEAD recheck required before merge"
    ]


def audit(repo: str, max_prs: int = 250) -> dict:
    base = repo_path(repo)
    main_sha = api_get(base + "/branches/main")["commit"]["sha"]
    listings = all_open_prs(base)
    if len(listings) > max_prs:
        # Fail closed rather than pretending a partial PR inventory is complete.
        raise RuntimeError(f"Open PRs {len(listings)} exceeds max_prs={max_prs}")
    rows = []
    for brief in listings:
        number = int(brief["number"])
        pr = api_get(f"{base}/pulls/{number}")
        head = pr["head"]["sha"]
        run_data = api_get(
            f"{base}/actions/runs?head_sha={quote(head)}&event=pull_request&per_page=100"
        )
        ci = latest_head_ci(run_data.get("workflow_runs", []), head)
        category, blockers = classify(pr, ci)
        rows.append({
            "number": number, "title": pr.get("title"),
            "url": pr.get("html_url"), "draft": bool(pr.get("draft")),
            "base": pr["base"]["ref"], "head_sha": head,
            "mergeable_state": pr.get("mergeable_state"),
            "ci": ci, "category": category, "blockers": blockers,
        })
    # Detect concurrent main changes: snapshot invalidated if main HEAD moved.
    final_sha = api_get(base + "/branches/main")["commit"]["sha"]
    return {
        "schema": 1, "repository": repo,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "main_sha_at_start": main_sha, "main_sha_at_end": final_sha,
        "main_stable_during_scan": main_sha == final_sha,
        "open_pr_count": len(listings), "scanned_pr_count": len(rows),
        "category_counts": dict(Counter(x["category"] for x in rows)),
        "automated_merge_approved": False,
        "warning": "CI success is engineering evidence, never proof of stronger gameplay; manual review is mandatory.",
        "pull_requests": rows,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default="sstxww/reinforcement-learning")
    p.add_argument("--max-prs", type=int, default=250)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.repo, args.max_prs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "pull_requests"}, ensure_ascii=False))
    if not result["main_stable_during_scan"]:
        print("NOTICE: main moved during audit; recheck against current main before any merge")


if __name__ == "__main__":
    main()
