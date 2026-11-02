"""Read-only exact-main CI gate. This is NOT a merge lease or PPO strength proof."""
from __future__ import annotations
import argparse
import json
import re
import urllib.request

REPOSITORY = "sstxww/reinforcement-learning"
WORKFLOW = "CI - full-match gate"
REQUIRED_STEPS = (
    "Unit tests and PR evidence",
    "Install pinned engine and verified patch",
    "Confirm engine layout",
    "Real full eight-seat simulated match",
)
SHA = re.compile(r"[0-9a-f]{40}\Z")


def get_sha(branch: dict) -> str:
    value = branch.get("commit", {}).get("sha")
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError("Missing trustworthy main SHA")
    return value


def select_run(sha: str, runs: list[dict]) -> dict:
    matches = [r for r in runs if r.get("head_sha") == sha
               and r.get("name") == WORKFLOW and r.get("head_branch") == "main"
               and r.get("event") == "push"]
    if not matches:
        raise ValueError("No exact-main-head push CI; older green results are invalid")
    run = max(matches, key=lambda r: (int(r.get("id", 0)), int(r.get("run_attempt", 0))))
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        raise ValueError("Current main CI is pending, failed or cancelled")
    if type(run.get("id")) is not int or run["id"] <= 0:
        raise ValueError("Invalid workflow run id")
    return run


def verify(branch: dict, runs: list[dict], jobs: list[dict], final_branch: dict) -> dict:
    sha = get_sha(branch)
    run = select_run(sha, runs)
    if get_sha(final_branch) != sha:
        raise ValueError("main moved during the audit; refresh all evidence")
    matching_jobs = [j for j in jobs if j.get("name") == "tests-and-full-match"]
    if len(matching_jobs) != 1 or matching_jobs[0].get("conclusion") != "success":
        raise ValueError("Missing or unsuccessful full-match CI job")
    steps = matching_jobs[0].get("steps")
    if not isinstance(steps, list):
        raise ValueError("Missing CI job step details")
    for name in REQUIRED_STEPS:
        found = [step for step in steps if step.get("name") == name]
        if len(found) != 1 or found[0].get("conclusion") != "success":
            raise ValueError("Missing or failed required CI step: " + name)
    return {"main_sha": sha, "ready_for_integration_review": True,
            "run_id": run["id"], "run_url": run.get("html_url"),
            "required_steps_verified": list(REQUIRED_STEPS),
            "scope": "CI precheck only, not merge lease or game receipt attestation"}


def get_json(path: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/repos/" + REPOSITORY + path,
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "AutoTavern-V7-readonly-main-ci"})
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)


def audit() -> dict:
    branch = get_json("/branches/main")
    sha = get_sha(branch)
    all_runs = get_json("/actions/runs?branch=main&per_page=100")
    runs = all_runs.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("Malformed workflow run collection")
    selected = select_run(sha, runs)
    jobs_data = get_json(f"/actions/runs/{selected['id']}/jobs?filter=latest&per_page=100")
    jobs = jobs_data.get("jobs")
    if not isinstance(jobs, list) or jobs_data.get("total_count", 0) > 100:
        raise ValueError("Incomplete or malformed workflow job collection")
    return verify(branch, runs, jobs, get_json("/branches/main"))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out")
    args = p.parse_args()
    try:
        result = audit()
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(json.dumps({"ready_for_integration_review": False, "reason": str(exc)}))
        raise SystemExit(2) from exc
    print(json.dumps(result, sort_keys=True))
    if args.out:
        from pathlib import Path
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
