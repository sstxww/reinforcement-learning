"""Fail-closed, read-only triage of an AutoTavern pull-request backlog.

This module deliberately *never* merges a PR or treats CI as proof of model
strength. It consumes GitHub API snapshots, not stored credentials, and yields
an audit report that a human integrator must independently verify.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

_FULL_GAME_CI = "CI - full-match gate"


def _ref(payload: dict[str, Any], key: str, nested: str) -> Any:
    value = payload.get(key)
    if isinstance(value, dict):
        return value.get(nested)
    return value


def inspect_pr(pr: dict[str, Any], runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Identify *pre-review* blockers only; never authorize a merge."""
    head_sha = pr.get("head_sha") or _ref(pr, "head", "sha")
    base = _ref(pr, "base", "ref")
    number = pr.get("number")
    blockers: list[str] = []
    if not isinstance(number, int) or number < 1:
        blockers.append("missing_pr_number")
    if not isinstance(head_sha, str) or len(head_sha) != 40:
        blockers.append("missing_exact_head_sha")
    if pr.get("state") != "open":
        blockers.append("not_open")
    if pr.get("draft") is not False:
        blockers.append("draft_or_unknown_draft_state")
    if base != "main":
        blockers.append("stacked_or_unknown_base_dependency")
    if pr.get("mergeable") is not True:
        blockers.append("conflict_or_unresolved_mergeability")

    same_head = [
        run for run in runs
        if run.get("head_sha") == head_sha
        and run.get("name") == _FULL_GAME_CI
        and run.get("event") == "pull_request"
    ]
    exact_green = any(
        run.get("status") == "completed" and run.get("conclusion") == "success"
        for run in same_head
    )
    if not exact_green:
        blockers.append(
            "latest_head_full_match_ci_unverified" if same_head
            else "no_latest_head_full_match_pr_ci"
        )

    return {
        "number": number,
        "title": pr.get("title"),
        "base": base,
        "head_sha": head_sha,
        "observed_latest_head_ci": [
            {"id": run.get("id"), "status": run.get("status"),
             "conclusion": run.get("conclusion")}
            for run in same_head
        ],
        "pre_review_blockers": blockers,
        "status": "blocked" if blockers else "requires_independent_manual_review",
        "merge_authorized": False,
        "mandatory_manual_checks": [
            "re-read live main and exact PR HEAD at merge time",
            "independently inspect full diff, dependencies, secrets, model interfaces",
            "validate genuine session-owned full-match receipt and raw-vs-fallback attribution",
            "verify compatible checkpoint restore and standalone candidate evidence if model is affected",
            "resolve cross-session integration ownership and branch rules",
            "use GitHub expected-head-SHA merge only after all gates pass",
            "confirm post-merge main CI success",
        ],
    }


def build_report(prs: list[dict[str, Any]], runs: list[dict[str, Any]]) -> dict[str, Any]:
    audited = [inspect_pr(p, runs) for p in prs]
    histogram = Counter(reason for p in audited for reason in p["pre_review_blockers"])
    return {
        "schema": 1,
        "scope": "read_only_pre_review_no_merge_authority",
        "sample_size": len(prs),
        "blocked": sum(p["status"] == "blocked" for p in audited),
        "needs_manual_review": sum(p["status"] == "requires_independent_manual_review" for p in audited),
        "blocker_counts": dict(sorted(histogram.items())),
        "pull_requests": audited,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prs", type=Path, required=True,
                        help="JSON list, REST pulls list or connector {result:{issues:[...]}}")
    parser.add_argument("--runs", type=Path, required=True,
                        help="JSON list or REST {workflow_runs:[...]} status snapshot")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw_prs = json.loads(args.prs.read_text(encoding="utf-8"))
    raw_runs = json.loads(args.runs.read_text(encoding="utf-8"))
    prs = raw_prs.get("result", {}).get("issues", []) if isinstance(raw_prs, dict) and "result" in raw_prs else raw_prs
    runs = raw_runs.get("workflow_runs", []) if isinstance(raw_runs, dict) else raw_runs
    if not isinstance(prs, list) or not isinstance(runs, list):
        raise ValueError("Expected PR and workflow-run lists")
    report = build_report(prs, runs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("sample_size", "blocked", "needs_manual_review", "blocker_counts")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
