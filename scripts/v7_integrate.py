"""Fail-closed V7 manual serial PR integration gate.

This is a cooperating-actor serialization tool, not GitHub branch protection.
It does not execute the pull request's code or promote model checkpoints.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SHA = re.compile(r"[0-9a-f]{40}\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
REQUIRED_STEPS = {
    "Unit tests and PR evidence",
    "Confirm engine layout",
    "Real full eight-seat simulated match",
}


class GateError(RuntimeError):
    """A required gate is absent or unverifiable."""


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise GateError(reason)


class GitHubAPI:
    def __init__(self, repo: str, token: str):
        require(bool(REPOSITORY.fullmatch(repo)) and
                all(part not in (".", "..") for part in repo.split("/")),
                "invalid repository name")
        require(bool(token), "GH_TOKEN not configured")
        self.root = f"https://api.github.com/repos/{repo}"
        self.token = token

    def request(self, path: str, *, method: str = "GET", body: dict | None = None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = Request(
            self.root + path,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "AutoTavern-V7-Serial-Integration",
                **({"Content-Type": "application/json"} if data is not None else {}),
            },
        )
        try:
            with urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as err:
            # Do not print the token or untrusted API error response body.
            raise GateError(f"GitHub API {method} {path.split('?')[0]} HTTP {err.code}") from err


def inspect(api: GitHubAPI, *, pr_number: int, head_sha: str, main_sha: str) -> dict:
    require(pr_number > 0, "invalid PR number")
    require(bool(SHA.fullmatch(head_sha)), "expected PR head must be a 40-char SHA")
    require(bool(SHA.fullmatch(main_sha)), "expected main must be a 40-char SHA")

    main = api.request("/branches/main")
    require(main.get("commit", {}).get("sha") == main_sha,
            "main advanced; rebase/re-run exact-base CI")
    pr = api.request(f"/pulls/{pr_number}")
    require(pr.get("state") == "open" and not pr.get("draft"),
            "PR must be open and ready for review")
    require(pr.get("base", {}).get("ref") == "main", "PR must target main")
    require(pr.get("base", {}).get("sha") == main_sha,
            "PR base SHA differs from current main")
    require(pr.get("head", {}).get("sha") == head_sha, "PR head SHA changed")
    require(pr.get("mergeable") is True and pr.get("mergeable_state") == "clean",
            "PR not cleanly mergeable or mergeability pending")
    require(not pr.get("requested_reviewers") and not pr.get("requested_teams"),
            "pending reviewer requests")

    reviews = api.request(f"/pulls/{pr_number}/reviews?per_page=100")
    latest = {}
    for review in reviews:
        if review.get("user", {}).get("login"):
            latest[review["user"]["login"]] = review.get("state")
    require("CHANGES_REQUESTED" not in latest.values(),
            "unresolved changes-requested review")

    query = urlencode({"event": "pull_request", "head_sha": head_sha, "per_page": 100})
    runs = api.request(f"/actions/workflows/ci.yml/runs?{query}").get("workflow_runs", [])
    matching = [
        r for r in runs
        if r.get("status") == "completed"
        and r.get("conclusion") == "success"
        and r.get("head_sha") == head_sha
        and any(p.get("number") == pr_number
                and p.get("head", {}).get("sha") == head_sha
                and p.get("base", {}).get("sha") == main_sha
                for p in r.get("pull_requests", []))
    ]
    require(bool(matching),
            "no successful full-match CI for this exact PR head + main base")
    selected = max(matching, key=lambda r: r.get("id", 0))
    run_id = selected["id"]
    jobs = api.request(f"/actions/runs/{run_id}/jobs?per_page=100").get("jobs", [])
    require(any(j.get("name") == "tests-and-full-match"
                and j.get("status") == "completed"
                and j.get("conclusion") == "success"
                and REQUIRED_STEPS.issubset({
                    step.get("name") for step in j.get("steps", [])
                    if step.get("conclusion") == "success"
                }) for j in jobs),
            "successful CI lacks verified unit, engine, full-match job steps")
    artifacts = api.request(f"/actions/runs/{run_id}/artifacts?per_page=100").get(
        "artifacts", [])
    require(any(a.get("name") == f"ci-full-match-{run_id}"
                and not a.get("expired") and a.get("size_in_bytes", 0) > 0
                for a in artifacts),
            "full-match CI receipt artifact absent/empty/expired")

    # A second read refuses changed mutable refs before the optional write.
    latest_main = api.request("/branches/main")
    latest_pr = api.request(f"/pulls/{pr_number}")
    require(latest_main.get("commit", {}).get("sha") == main_sha
            and latest_pr.get("head", {}).get("sha") == head_sha
            and latest_pr.get("base", {}).get("sha") == main_sha
            and latest_pr.get("state") == "open"
            and not latest_pr.get("draft"),
            "race detected during preflight")
    return {"pr": pr_number, "head": head_sha, "main": main_sha,
            "ci_run": selected.get("html_url"), "ci_run_id": run_id}


def run(api: GitHubAPI, *, pr_number: int, head_sha: str,
        main_sha: str, merge: bool = False) -> dict:
    result = inspect(api, pr_number=pr_number, head_sha=head_sha, main_sha=main_sha)
    if not merge:
        return {"status": "preflight_only", **result}
    # GitHub merge API conditionally compares PR HEAD. This is NOT a main
    # branch CAS; external main mergers must be excluded separately.
    merged = api.request(f"/pulls/{pr_number}/merge", method="PUT",
                         body={"sha": head_sha, "merge_method": "squash",
                               "commit_title": f"V7 validated PR #{pr_number}"})
    require(merged.get("merged") is True and bool(merged.get("sha")),
            "GitHub did not confirm merge")
    pr = api.request(f"/pulls/{pr_number}")
    main = api.request("/branches/main")
    require(pr.get("merged") is True
            and main.get("commit", {}).get("sha") == merged["sha"],
            "merge accepted but main verification incomplete; inspect GitHub directly")
    return {"status": "merged_main_ci_pending",
            "merge_sha": merged["sha"], **result}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--main", required=True)
    parser.add_argument("--merge", action="store_true")
    args = parser.parse_args()
    try:
        response = run(GitHubAPI(os.environ.get("GITHUB_REPOSITORY", ""),
                                 os.environ.get("GH_TOKEN", "")),
                       pr_number=args.pr, head_sha=args.head, main_sha=args.main,
                       merge=args.merge)
    except GateError as exc:
        print(f"V7 integration BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(response, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
