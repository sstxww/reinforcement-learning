"""Fail-closed post-merge verification of the *current* main CI.

This is an evidence checker, not an integration lock, PR merger, or model
strength evaluation. Its inputs must come from live GitHub API responses.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SHA = re.compile(r"[0-9a-f]{40}\Z")
REQUIRED_STEPS = (
    "Unit tests and PR evidence",
    "Install pinned engine and verified patch",
    "Confirm engine layout",
    "Real full eight-seat simulated match",
    "Preserve CI evidence",
)


def audit(main: dict[str, Any], run: dict[str, Any], jobs: dict[str, Any],
          artifacts: dict[str, Any]) -> dict[str, Any]:
    """Report success only for an exact-main, completed, genuine push CI run."""
    errors: list[str] = []
    sha = (main.get("commit") or {}).get("sha")
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        errors.append("current main SHA unavailable or invalid")
    if main.get("name") != "main":
        errors.append("branch response is not main")

    run_id = run.get("id")
    if run.get("head_sha") != sha:
        errors.append("run head_sha does not match live main")
    if run.get("head_branch") != "main" or run.get("event") != "push":
        errors.append("run is not a main push")
    if run.get("name") != "CI - full-match gate":
        errors.append("unexpected workflow")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        errors.append("main run is not completed SUCCESS")
    if not isinstance(run_id, int) or run_id <= 0:
        errors.append("run ID is unavailable")

    job_list = jobs.get("jobs") if isinstance(jobs, dict) else None
    if not isinstance(job_list, list):
        errors.append("jobs payload unavailable")
        job_list = []
    full_jobs = [j for j in job_list if isinstance(j, dict)
                 and j.get("name") == "tests-and-full-match"]
    if len(full_jobs) != 1:
        errors.append("expected exactly one full-match job")
    else:
        job = full_jobs[0]
        if job.get("status") != "completed" or job.get("conclusion") != "success":
            errors.append("full-match job incomplete or unsuccessful")
        steps = job.get("steps")
        if not isinstance(steps, list):
            errors.append("full-match job steps unavailable")
        else:
            for name in REQUIRED_STEPS:
                matches = [s for s in steps if isinstance(s, dict) and s.get("name") == name]
                if len(matches) != 1 or matches[0].get("status") != "completed" or matches[0].get("conclusion") != "success":
                    errors.append(f"required step not successful: {name}")

    a_list = artifacts.get("artifacts") if isinstance(artifacts, dict) else None
    if not isinstance(a_list, list):
        errors.append("artifacts payload unavailable")
        a_list = []
    expected_name = f"ci-full-match-{run_id}"
    active = [a for a in a_list if isinstance(a, dict) and a.get("name") == expected_name
              and a.get("expired") is False and a.get("size_in_bytes", 0) > 0]
    if len(active) != 1:
        errors.append("verified run's temporary receipt artifact absent, empty, or expired")

    return {
        "schema": 1,
        "main_sha": sha,
        "workflow_run_id": run_id,
        "workflow_url": run.get("html_url"),
        "required_job": "tests-and-full-match",
        "required_steps": list(REQUIRED_STEPS),
        "receipt_artifact_name": expected_name,
        "decision": "main_ci_verified" if not errors else "blocked",
        "blockers": errors,
        "proof_scope": "CI infrastructure + completed baseline canary step; not model performance",
        "integration_lock_verified": False,
        "model_improvement_verified": False,
    }


def main_cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", required=True, type=Path)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--jobs", required=True, type=Path)
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = [json.loads(p.read_text(encoding="utf-8"))
               for p in (args.main, args.run, args.jobs, args.artifacts)]
    result = audit(*payload)
    formatted = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(formatted, encoding="utf-8")
    print(formatted)
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main_cli())
