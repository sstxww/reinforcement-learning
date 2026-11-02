"""Fail-closed PR gate for a *serialized* V7 main integration workflow.

The fixed Actions concurrency group serializes cooperating V7 integrations,
not arbitrary admin actions. Never mistake a PR's old success for HEAD CI.
No training, model promotion, or merge is authorized by dry-run results alone.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.request


class GateError(ValueError):
    pass


def require(ok: bool, why: str) -> None:
    if not ok:
        raise GateError(why)


def validate(pr: dict, ref: dict, ci: dict, jobs: dict, reviews: list,
             *, repo: str, number: int, head: str, main: str) -> dict:
    """Validate frozen GitHub API snapshots; never infer a passing check."""
    require(pr.get("state") == "open" and pr.get("draft") is False, "PR must be open and ready")
    require(pr.get("number") == number, "PR number mismatch")
    require(pr.get("base", {}).get("ref") == "main", "PR targets a dependency, not main")
    require(pr.get("base", {}).get("sha") == main, "PR base differs from expected main")
    require(pr.get("head", {}).get("sha") == head, "PR head changed")
    require(pr.get("head", {}).get("repo", {}).get("full_name") == repo,
            "Cross-repository head is not supported by this integration gate")
    require(pr.get("mergeable") is True and pr.get("mergeable_state") == "clean",
            "PR is conflicting, blocked, or mergeability is unknown")
    require(ref.get("object", {}).get("sha") == main, "Live main changed before integration")
    author = pr.get("user", {}).get("login", "").casefold()
    approved: set[str] = set()
    latest = {}
    for review in reviews:
        who = str(review.get("user", {}).get("login", "")).casefold()
        if who:
            latest[who] = review
    for who, review in latest.items():
        if (who != author and review.get("state") == "APPROVED"
                and review.get("commit_id") == head):
            approved.add(who)
    require(bool(approved), "No independent APPROVED review on exact PR head")
    require(ci.get("name") == "CI - full-match gate", "Unexpected CI workflow")
    require(ci.get("event") == "pull_request", "CI must run on pull_request")
    require(ci.get("status") == "completed" and ci.get("conclusion") == "success",
            "Latest-head CI has not succeeded")
    related = [p for p in ci.get("pull_requests", []) if p.get("number") == number]
    require(bool(related), "CI run is not linked to target PR")
    # PR CI can run on a synthetic merge SHA; then pin its recorded PR head.
    run_exact = ci.get("head_sha") == head or any(
        p.get("head", {}).get("sha") == head for p in related)
    require(run_exact, "CI does not prove the exact PR head SHA")
    proof = False
    for job in jobs.get("jobs", []):
        if job.get("name") != "tests-and-full-match" or job.get("conclusion") != "success":
            continue
        steps = {s.get("name"): s.get("conclusion") for s in job.get("steps", [])}
        if (steps.get("Unit tests and PR evidence") == "success"
                and steps.get("Real full eight-seat simulated match") == "success"):
            proof = True
    require(proof, "No successful full-game + unit-test job on this CI run")
    return {"safe_for_serial_review": True, "pr": number, "head": head,
            "main_before": main, "reviewers": sorted(approved),
            "ci_run": ci.get("html_url"), "warning":
            "Only serial V7 workflow is synchronized; direct admin merges are outside this lock."}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default="sstxww/reinforcement-learning")
    p.add_argument("--number", type=int, required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--main", required=True)
    p.add_argument("--ci-run", type=int, required=True)
    p.add_argument("--merge", action="store_true")
    a = p.parse_args()
    token = os.getenv("GH_TOKEN", "")
    require(bool(token), "GH_TOKEN is required")
    require(a.repo == "sstxww/reinforcement-learning", "Unexpected repository")
    require(len(a.head) == len(a.main) == 40
            and all(c in "0123456789abcdef" for c in a.head + a.main),
            "Expected full lowercase commit SHA values")
    api_base = "https://api.github.com/repos/" + a.repo

    def api(path: str, *, method: str = "GET", payload: dict | None = None):
        body = None if payload is None else json.dumps(payload).encode()
        req = urllib.request.Request(api_base + path, data=body, method=method,
                                     headers={"Authorization": "Bearer " + token,
                                              "Accept": "application/vnd.github+json",
                                              "X-GitHub-Api-Version": "2022-11-28",
                                              "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.load(r)

    path = "/pulls/" + str(a.number)
    pr = api(path)
    ref = api("/git/ref/heads/main")
    ci = api("/actions/runs/" + str(a.ci_run))
    jobs = api("/actions/runs/" + str(a.ci_run) + "/jobs?per_page=100")
    reviews = api(path + "/reviews?per_page=100")
    result = validate(pr, ref, ci, jobs, reviews,
                      repo=a.repo, number=a.number, head=a.head, main=a.main)
    print(json.dumps(result, sort_keys=True))
    if not a.merge:
        return
    require(os.getenv("V7_SERIAL_INTEGRATOR") == "true",
            "Missing protected integration-job flag")
    require(os.getenv("GITHUB_REF") == "refs/heads/main",
            "Integration requires main workflow ref")
    # Fixed Actions concurrency covers cooperating V7 writers, not external admins.
    require(api("/git/ref/heads/main")["object"]["sha"] == a.main,
            "Main advanced while validating PR; abort without merging")
    require(api(path)["head"]["sha"] == a.head, "PR changed while validating; abort")
    merged = api(path + "/merge", method="PUT",
                 payload={"sha": a.head, "merge_method": "squash",
                          "commit_title": "V7 verified PR #" + str(a.number)})
    require(merged.get("merged") is True, "GitHub did not confirm merge")
    print(json.dumps({"merged": True, "sha": merged.get("sha"),
                      "pr": a.number, "needs_main_ci": True}))


if __name__ == "__main__":
    main()
