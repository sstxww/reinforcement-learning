#!/usr/bin/env python3
"""V7 fail-closed GitHub Actions-only serial PR merge gate; no PR-head code execution."""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CI = "CI - full-match gate"
STEPS = ("Unit tests and PR evidence", "Install pinned engine and verified patch",
         "Confirm engine layout", "Real full eight-seat simulated match",
         "Preserve CI evidence")

PROTECTED_EVIDENCE = frozenset({
    ".github/workflows/ci.yml",
    ".github/workflows/v7-serialized-integrator.yml",
    "scripts/check_pr_evidence.py",
    "scripts/v7_serial_integrator.py",
    "tavern_ai/receipt_integrity.py",
    "tavern_ai/validate_receipt.py",
})

class GateError(RuntimeError):
    pass

def check_sensitive_paths(files):
    """Do not trust a PR's self-modified CI or integration checks."""
    if len(files) >= 100:
        raise GateError("Changed-file list might be truncated")
    touched = {f.get("filename") for f in files}
    blocked = sorted(PROTECTED_EVIDENCE.intersection(touched))
    if blocked:
        raise GateError("PR changes its evidence/integration gate; requires separate review: " + ", ".join(blocked))

def sha(value):
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise GateError("Expected immutable full 40-hex SHA")
    return value

def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def check_pr(pr, repository, number, expected_head, expected_main):
    if pr.get("number") != number or pr.get("state") != "open" or pr.get("draft") is not False:
        raise GateError("Incorrect PR, closed or Draft")
    if pr.get("base", {}).get("ref") != "main" or pr["base"].get("sha") != expected_main:
        raise GateError("PR target is not exact latest main")
    head = pr.get("head", {})
    if head.get("sha") != expected_head or head.get("repo", {}).get("full_name") != repository:
        raise GateError("PR head SHA or source repository mismatch")
    if pr.get("mergeable") is not True or pr.get("mergeable_state") != "clean":
        raise GateError("GitHub has not confirmed clean mergeability")

def check_reviews(reviews, author, head):
    latest = {}
    for review in sorted(reviews, key=lambda r: r.get("submitted_at") or ""):
        user = (review.get("user") or {}).get("login")
        if user and review.get("state") in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            latest[user] = review
    if any(r["state"] == "CHANGES_REQUESTED" for r in latest.values()):
        raise GateError("Unresolved change request")
    if not any(user != author and r["state"] == "APPROVED"
               and r.get("commit_id") == head for user, r in latest.items()):
        raise GateError("No independent approval of current head commit")

def check_run(runs, number, head, main_time):
    matching = [r for r in runs
                if r.get("event") == "pull_request" and r.get("head_sha") == head
                and r.get("name") == CI
                and r.get("path", "").split("@")[0].endswith(".github/workflows/ci.yml")
                and number in [p.get("number") for p in r.get("pull_requests", [])]]
    if not matching:
        raise GateError("Missing exact-head PR CI")
    run = max(matching, key=lambda r: r.get("created_at") or "")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        raise GateError("Latest exact-head PR CI not green")
    if timestamp(run.get("run_started_at") or run["created_at"]) < timestamp(main_time):
        raise GateError("Green CI predates latest main change")
    return run

def check_jobs(jobs):
    matches = [j for j in jobs if j.get("name") == "tests-and-full-match"]
    if len(matches) != 1 or matches[0].get("conclusion") != "success":
        raise GateError("Required eight-player job absent or failed")
    steps = {s.get("name"): s.get("conclusion") for s in matches[0].get("steps", [])}
    for name in STEPS:
        if steps.get(name) != "success":
            raise GateError("Missing passing job step: " + name)

class GitHub:
    def __init__(self, repo, token):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not token:
            raise GateError("Repository or GitHub token unavailable")
        self.repo, self.token = repo, token

    def call(self, path, method="GET", body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = Request("https://api.github.com/repos/" + self.repo + path, data=data,
                      method=method, headers={
                          "Authorization": "Bearer " + self.token,
                          "Accept": "application/vnd.github+json",
                          "X-GitHub-Api-Version": "2022-11-28",
                          "User-Agent": "autotavern-v7-serial-integrator",
                          **({"Content-Type": "application/json"} if data else {})})
        try:
            with urlopen(req, timeout=20) as response:
                return json.load(response)
        except (HTTPError, URLError, ValueError) as error:
            raise GateError("GitHub API failed " + method + " " + path.split("?")[0] +
                            " (" + type(error).__name__ + ")") from error

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--head", required=True)
    parser.add_argument("--main", required=True)
    parser.add_argument("--apply", action="store_true")
    a = parser.parse_args()
    if a.pr < 1:
        raise GateError("Invalid PR number")
    head, base = sha(a.head), sha(a.main)
    if os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch" or os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise GateError("Must execute only via manual workflow on main")
    api = GitHub(os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GITHUB_TOKEN", ""))
    if api.call("/branches/main")["commit"]["sha"] != base:
        raise GateError("Main moved before integration")
    pr = api.call("/pulls/" + str(a.pr))
    check_pr(pr, api.repo, a.pr, head, base)
    check_sensitive_paths(api.call("/pulls/" + str(a.pr) + "/files?per_page=100"))
    reviews = api.call("/pulls/" + str(a.pr) + "/reviews?per_page=100")
    if len(reviews) >= 100:
        raise GateError("Paginated review evidence is incomplete")
    check_reviews(reviews, pr["user"]["login"], head)
    commit = api.call("/commits/" + base)
    runs = api.call("/actions/runs?event=pull_request&head_sha=" + head + "&per_page=100")
    if runs.get("total_count", 0) > 100:
        raise GateError("Paginated CI evidence is incomplete")
    run = check_run(runs["workflow_runs"], a.pr, head, commit["commit"]["committer"]["date"])
    jobs = api.call("/actions/runs/" + str(run["id"]) + "/jobs?per_page=100")
    if jobs.get("total_count", 0) > 100:
        raise GateError("Paginated job evidence is incomplete")
    check_jobs(jobs["jobs"])
    if api.call("/branches/main")["commit"]["sha"] != base or api.call("/pulls/" + str(a.pr))["head"]["sha"] != head:
        raise GateError("Main or PR head changed during final preflight")
    print(json.dumps({"preflight": "pass", "pr": a.pr, "head": head, "main": base,
                      "ci": run["html_url"]}), flush=True)
    if not a.apply:
        print("DRY_RUN: no merge performed")
        return
    # Only cooperating dispatches are serialized; direct merge API bypasses concurrency.
    response = api.call("/pulls/" + str(a.pr) + "/merge", "PUT",
                        {"sha": head, "merge_method": "squash"})
    if response.get("merged") is not True:
        raise GateError("GitHub did not confirm merge")
    merged = sha(response["sha"])
    print(json.dumps({"merged": True, "main_sha": merged}), flush=True)
    if api.call("/branches/main")["commit"]["sha"] != merged:
        raise GateError("Main advanced after merge; verify new main separately")
    for _ in range(100):
        runs = api.call("/actions/runs?event=push&branch=main&per_page=40")["workflow_runs"]
        matches = [r for r in runs if r.get("head_sha") == merged and r.get("name") == CI]
        if matches:
            r = max(matches, key=lambda x: x.get("created_at") or "")
            if r["status"] == "completed":
                if r["conclusion"] == "success":
                    print(json.dumps({"main_ci": "success", "run": r["html_url"]}))
                    return
                raise GateError("Merge succeeded, main CI did not pass: " + r["html_url"])
        time.sleep(12)
    raise GateError("Merge succeeded, main CI still unverified after 20 minutes")

if __name__ == "__main__":
    try:
        main()
    except GateError as exc:
        print("V7_GATE_BLOCKED: " + str(exc), file=sys.stderr)
        sys.exit(1)
