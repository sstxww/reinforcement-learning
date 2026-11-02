"""Fail-closed V7 PR readiness audit, without modifying PRs or merging main.

This tool is intentionally read-only. GitHub checks must correspond to the exact
PR head, and the PR must still target the exact observed main SHA. A green
historical run, queued job, or artifact-only result is not a merge approval.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from tavern_ai.receipt_integrity import validate_integrity

REPO = "sstxww/reinforcement-learning"
CI_NAME = "CI - full-match gate"
ENGINE_HASH = "6d8712c93022ba11"


def github_get(path: str) -> object:
    if not path.startswith("/") or "//" in path:
        raise ValueError("API path must be relative to GitHub API")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "autotavern-v7-readonly-gate",
               "X-GitHub-Api-Version": "2022-11-28"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    request = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)


def full_game_receipt(record: dict, agent_id: str) -> None:
    validate_integrity(record)
    if record["agent_id"] != agent_id:
        raise ValueError("Receipt belongs to another session")
    if record.get("engine_source_hash") != ENGINE_HASH:
        raise ValueError("Receipt uses another engine")
    if record.get("seat", 0) != 0:
        raise ValueError("Receipt is not for seat zero")
    if record.get("policy") == "model" and record.get("model_sha256") is None:
        raise ValueError("Raw model identity is missing")
    if record.get("raw_model_only") is False or record.get("guarded") is True:
        raise ValueError("Assisted or guarded model receipt")
    for key in ("guard_forced_end", "guard_forced_ends", "fallback_actions",
                "fallback_count", "guard_interventions", "forced_end_count"):
        value = record.get(key, 0)
        if type(value) is not int or value != 0:
            raise ValueError("Guard/fallback activity must be zero: " + key)


def assess(pr: dict, main_sha: str, expected_main: str, expected_head: str,
           runs: list[dict], jobs_by_run: dict[int, dict],
           changed_files: list[str], receipt_path: str, receipt: dict) -> dict:
    failures: list[str] = []
    def require(condition: bool, reason: str) -> None:
        if not condition:
            failures.append(reason)

    number = pr.get("number")
    head = pr.get("head") or {}
    base = pr.get("base") or {}
    branch = head.get("ref", "")
    pieces = branch.split("/")
    session = pieces[1] if len(pieces) >= 3 and pieces[0] == "agent" else None
    require(pr.get("state") == "open" and pr.get("draft") is False, "PR not open and ready")
    require(pr.get("mergeable") is True and pr.get("mergeable_state") == "clean",
            "PR mergeability is not demonstrably clean")
    require(base.get("ref") == "main", "PR does not target main")
    require(main_sha == expected_main and base.get("sha") == expected_main,
            "main or PR base has changed: rebase and rerun")
    require(head.get("sha") == expected_head, "PR head changed: check exact current head")
    require((head.get("repo") or {}).get("full_name") == REPO, "PR head is not in the authorized repository")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", str(expected_head))), "Invalid expected head SHA")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", str(expected_main))), "Invalid expected main SHA")
    require(session is not None, "PR does not use isolated agent/<session>/... branch")
    require(receipt_path.startswith(f"experiments/{session}/") if session else False,
            "Receipt path must belong to PR session")
    require(receipt_path.endswith(".json") and ".." not in receipt_path,
            "Receipt must be a valid JSON path")
    require(receipt_path in changed_files, "Independent receipt is absent from PR diff")
    require(len(changed_files) > 0, "PR has no changes")
    require(not any(f.endswith((".zip", ".pt", ".pth", ".pkl")) for f in changed_files),
            "Large model weights / pickle files must not enter Git history")
    try:
        full_game_receipt(receipt, session or "")
    except (ValueError, TypeError, KeyError) as exc:
        failures.append("Receipt integrity: " + str(exc))

    matching_runs = [r for r in runs if r.get("name") == CI_NAME
                     and r.get("head_sha") == expected_head
                     and r.get("event") == "pull_request"]
    # Never substitute a green older run for a later failed/pending run.
    matching_runs.sort(key=lambda r: (r.get("created_at") or "", r.get("id") or 0), reverse=True)
    selected = matching_runs[0] if matching_runs else None
    require(selected is not None, "No latest-head pull_request full-match CI run")
    if selected:
        require(selected.get("status") == "completed" and selected.get("conclusion") == "success",
                "Latest-head CI did not complete successfully")
        batch = jobs_by_run.get(selected["id"]) or {}
        jobs = batch.get("jobs") or []
        require(batch.get("total_count") == len(jobs) and len(jobs) > 0,
                "CI job listing missing/truncated or empty")
        require(all(j.get("status") == "completed" and j.get("conclusion") == "success"
                    for j in jobs), "CI contains unfinished/unsuccessful jobs")
        require(any(j.get("name") == "tests-and-full-match" for j in jobs),
                "CI is missing the actual full-game job")
    return {
        "schema": 1, "pr": number, "base_main_sha": main_sha, "expected_head_sha": expected_head,
        "session": session, "receipt": receipt_path,
        "ci_run": selected.get("html_url") if selected else None,
        "merge_performed": False, "review_and_exclusive_integration_lease_required": True,
        "ready_for_exclusive_integration_review": not failures, "blockers": failures,
    }


def run_check(pr_number: int, expected_main: str, expected_head: str, receipt_path: str) -> dict:
    if pr_number < 1 or pr_number > 1_000_000:
        raise ValueError("Invalid PR number")
    if not re.fullmatch(r"experiments/s-[0-9]{8}-[a-z0-9]+/[a-zA-Z0-9_.-]+\\.json", receipt_path):
        raise ValueError("Invalid or unsafe receipt path")
    prefix = "/repos/" + REPO
    main = github_get(prefix + "/branches/main")
    pr = github_get(prefix + "/pulls/" + str(pr_number))
    query = urllib.parse.urlencode({"head_sha": expected_head, "event": "pull_request", "per_page": 100})
    runs = github_get(prefix + "/actions/runs?" + query)
    changed = github_get(prefix + f"/pulls/{pr_number}/files?per_page=100")
    if not isinstance(changed, list) or len(changed) >= 100:
        raise ValueError("Changed-file listing incomplete; refuse ambiguous review")
    data = github_get(prefix + "/contents/" + urllib.parse.quote(receipt_path) +
                      "?ref=" + urllib.parse.quote(expected_head))
    import base64
    if data.get("encoding") != "base64":
        raise ValueError("Receipt bytes not supplied by GitHub")
    receipt = json.loads(base64.b64decode(data["content"]).decode("utf-8"))
    candidates = [r for r in runs.get("workflow_runs", []) if r.get("name") == CI_NAME
                  and r.get("head_sha") == expected_head and r.get("event") == "pull_request"]
    latest = max(candidates, key=lambda r: (r.get("created_at") or "", r.get("id") or 0),
                 default=None)
    jobs = {}
    if latest:
        jobs[latest["id"]] = github_get(prefix + f"/actions/runs/{latest['id']}/jobs?per_page=100")
    return assess(pr, main["commit"]["sha"], expected_main, expected_head,
                  runs.get("workflow_runs", []), jobs, [f["filename"] for f in changed],
                  receipt_path, receipt)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--expected-main", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = run_check(args.pr, args.expected_main, args.expected_head, args.receipt)
    except (ValueError, KeyError, TypeError, urllib.error.URLError) as exc:
        report = {"schema": 1, "pr": args.pr, "ready_for_exclusive_integration_review": False,
                  "merge_performed": False, "blockers": [str(exc)]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if not report["ready_for_exclusive_integration_review"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
