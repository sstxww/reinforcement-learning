"""V7 read-only pre-merge concurrency audit. NEVER grants or performs a merge.

A CAS coordination ref serializes only clients honoring it. No GitHub metadata
field, by itself, proves that all independent clients are blocked from calling
the direct PR merge API. This tool deliberately returns advisory findings,
not an authorization token. No destructive GitHub API calls are made.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from typing import Any

_SHA = re.compile(r"[a-f0-9]{40}\Z")
_REPO = "sstxww/reinforcement-learning"


def audit(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Find observable pre-merge hazards without implying global exclusivity."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    main = snapshot.get("main") or {}
    pr = snapshot.get("pr") or {}
    runs = snapshot.get("pr_runs") or []
    rulesets = snapshot.get("rulesets") or []
    problems: list[str] = []

    main_sha, head_sha = main.get("sha"), pr.get("head_sha")
    if not isinstance(main_sha, str) or not _SHA.fullmatch(main_sha):
        problems.append("main_sha_unverified")
    if not isinstance(head_sha, str) or not _SHA.fullmatch(head_sha):
        problems.append("pr_head_sha_unverified")
    if main.get("protected") is not True:
        problems.append("main_not_protected")
    if pr.get("base") != "main" or pr.get("state") != "open":
        problems.append("wrong_pr_target_or_state")
    if pr.get("draft") is not False:
        problems.append("draft_pr")
    if pr.get("mergeable") is not True:
        problems.append("mergeability_not_verified")
    matching = [
        row for row in runs if isinstance(row, dict)
        and row.get("head_sha") == head_sha
        and row.get("event") in ("pull_request", "merge_group")
        and row.get("status") == "completed"
        and row.get("conclusion") == "success"
    ] if isinstance(runs, list) else []
    if not matching:
        problems.append("no_successful_exact_head_pr_ci")
    # An active merge-queue ruleset is evidence of configuration, NOT evidence
    # that all users/apps and admins are unable to bypass it.
    queue_seen = any(
        isinstance(r, dict) and r.get("enforcement") == "active"
        and not r.get("bypass_actors")
        and any(isinstance(rule, dict) and rule.get("type") == "merge_queue"
                for rule in (r.get("rules") or []))
        for r in rulesets
    ) if isinstance(rulesets, list) else False
    if not queue_seen:
        problems.append("no_active_merge_queue_ruleset_observed")
    # A prior verified incident proves a lease alone was bypassed. Even an
    # apparently clean snapshot lacks proof that external writers cannot merge.
    problems.append("exclusive_merge_writer_authority_not_proven")
    return {
        "schema": 1,
        "main_sha": main_sha,
        "pr_head_sha": head_sha,
        "matching_ci_runs": [r.get("id") for r in matching],
        "active_queue_ruleset_observed": queue_seen,
        "problems": problems,
        "merge_authorized": False,
        "note": "Read-only audit. An enforced single entry, non-bypassable restrictions, "
                "reviews, current-main merged-code CI, and an actual live lease or "
                "merge queue must be verified separately before any merge.",
    }


def _gh_get(path: str) -> Any:
    # Deliberately uses GET only. Missing auth or HTTP 403 is not success.
    completed = subprocess.run(
        ["gh", "api", "-X", "GET", path],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return json.loads(completed.stdout)


def live_snapshot(pr_number: int) -> dict[str, Any]:
    if pr_number <= 0:
        raise ValueError("PR number must be positive")
    prefix = "repos/" + _REPO
    branch = _gh_get(f"{prefix}/branches/main")
    pull = _gh_get(f"{prefix}/pulls/{pr_number}")
    sha = pull["head"]["sha"]
    runs = _gh_get(f"{prefix}/actions/runs?head_sha={sha}&per_page=100")
    rules = _gh_get(f"{prefix}/rulesets?includes_parents=true")
    return {
        "main": {"sha": branch["commit"]["sha"], "protected": branch.get("protected")},
        "pr": {
            "head_sha": sha, "base": pull["base"]["ref"],
            "state": pull["state"], "draft": pull.get("draft"),
            "mergeable": pull.get("mergeable"),
        },
        "pr_runs": runs.get("workflow_runs", []),
        "rulesets": rules if isinstance(rules, list) else [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--snapshot", help="Offline JSON fixture")
    source.add_argument("--pr", type=int, help="Live read-only GitHub PR audit")
    args = parser.parse_args()
    try:
        if args.snapshot:
            from pathlib import Path
            data = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
        else:
            data = live_snapshot(args.pr)
        result = audit(data)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        result = {"schema": 1, "merge_authorized": False,
                  "problems": ["live_evidence_unavailable"], "error_type": type(exc).__name__}
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    # Fail closed; this code NEVER authorizes a PR merge.
    raise SystemExit(2)


if __name__ == "__main__":
    main()
