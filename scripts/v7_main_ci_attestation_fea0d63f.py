"""Read-only, fail-closed attestation of the *current* main SHA's CI.

A green PR run or a successful *older* main SHA is not post-merge CI proof.
This checks the live branch twice; it is NOT a merge lock, branch protection,
a verified download of the Actions artifact, or a model-strength certificate.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

REPOSITORY = "sstxww/reinforcement-learning"
REQUIRED_STEPS = (
    "Unit tests and PR evidence",
    "Install pinned engine and verified patch",
    "Confirm engine layout",
    "Real full eight-seat simulated match",
    "Preserve CI evidence",
)


def github_get(url: str) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AutoTavern-V7-main-CI-attestation-readonly",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=25) as response:
        return json.load(response)


def _main_sha(get, api: str) -> str:
    branch = get(f"{api}/branches/main")
    if not isinstance(branch, dict) or not isinstance(branch.get("commit"), dict):
        raise ValueError("Missing live main branch")
    sha = branch["commit"].get("sha")
    if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("Invalid main commit SHA")
    return sha


def attest(get=github_get, *, repository: str = REPOSITORY,
           expected_main_sha: str | None = None) -> dict:
    if repository != REPOSITORY:
        raise ValueError("Only the authorized repository may be audited")
    api = f"https://api.github.com/repos/{repository}"
    main_sha = _main_sha(get, api)
    if expected_main_sha is not None and main_sha != expected_main_sha:
        raise ValueError("Main moved since the requested snapshot")
    response = get(f"{api}/actions/runs?branch=main&per_page=100")
    if not isinstance(response, dict) or not isinstance(response.get("workflow_runs"), list):
        raise ValueError("Invalid Actions runs API result")
    rows = response["workflow_runs"]
    if len(rows) > 100:
        raise ValueError("Invalid first-page Actions runs count")
    matching = [r for r in rows if isinstance(r, dict)
                and r.get("head_sha") == main_sha
                and r.get("head_branch") == "main"
                and r.get("event") == "push"
                and r.get("name") == "CI - full-match gate"
                and r.get("path") == ".github/workflows/ci.yml"]
    if not matching:
        raise ValueError("No full-match CI run for exact current main SHA")
    if any(type(r.get("id")) is not int or type(r.get("run_attempt")) is not int
           for r in matching):
        raise ValueError("Invalid Actions run ID or attempt")
    current = max(matching, key=lambda r: (r["id"], r["run_attempt"]))
    if current.get("status") != "completed" or current.get("conclusion") != "success":
        raise ValueError("Latest exact-main CI is pending, cancelled, or unsuccessful")
    run_id = current["id"]
    jobs_response = get(f"{api}/actions/runs/{run_id}/jobs?per_page=100")
    if not isinstance(jobs_response, dict) or not isinstance(jobs_response.get("jobs"), list):
        raise ValueError("Invalid CI jobs API result")
    if jobs_response.get("total_count", 0) > 100:
        raise ValueError("Job list pagination incomplete")
    jobs = [j for j in jobs_response["jobs"] if isinstance(j, dict)
            and j.get("name") == "tests-and-full-match"]
    if len(jobs) != 1 or jobs[0].get("conclusion") != "success":
        raise ValueError("Required full-match job did not succeed")
    steps = jobs[0].get("steps")
    if not isinstance(steps, list) or any(not isinstance(s, dict) for s in steps):
        raise ValueError("Malformed job steps")
    for required in REQUIRED_STEPS:
        found = [s for s in steps if s.get("name") == required]
        if len(found) != 1 or found[0].get("conclusion") != "success":
            raise ValueError(f"Required successful CI step missing: {required}")
    if _main_sha(get, api) != main_sha:
        raise ValueError("Main changed while checking CI; retry from a fresh SHA")
    return {
        "schema": 1,
        "repository": repository,
        "main_sha": main_sha,
        "run_id": run_id,
        "run_attempt": current["run_attempt"],
        "run_url": current.get("html_url"),
        "job_url": jobs[0].get("html_url"),
        "status": "exact_main_ci_steps_verified",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "verified_step_names": list(REQUIRED_STEPS),
        "post_merge_artifact_bytes_verified": False,
        "merge_lock_held": False,
        "training_performed_by_this_audit": False,
        "model_improvement_claimed": False,
        "caveat": "Exact-main successful CI job/step metadata only. The main ref can advance after this audit; recheck immediately before an integration claim.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-main-sha", help="Fail if main changed")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = attest(expected_main_sha=args.expected_main_sha)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
