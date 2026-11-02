"""Fail-closed, read-only V7 preflight for *observable* merge admission settings.

A successful read alone is never a globally exclusive merge lease. This
audit deliberately cannot authorize or execute merges.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def audit(branch: dict, rulesets: list, expected_main_sha: str | None = None) -> dict:
    if not isinstance(branch, dict) or not isinstance(rulesets, list):
        raise ValueError("Expected branch object and ruleset list")
    blockers = []
    sha = (branch.get("commit") or {}).get("sha")
    if branch.get("name") != "main" or not isinstance(sha, str) or len(sha) != 40:
        blockers.append("Missing verifiable exact main SHA")
    if expected_main_sha is not None and sha != expected_main_sha:
        blockers.append("Main advanced since expected SHA")
    if branch.get("protected") is not True:
        blockers.append("Main is not protected; direct alternate merges are not excluded")
    protection = branch.get("protection") or {}
    if protection.get("enabled") is not True:
        blockers.append("Branch protection is not enabled")
    checks = protection.get("required_status_checks") or {}
    if checks.get("enforcement_level") in (None, "off") or not (
        checks.get("checks") or checks.get("contexts")
    ):
        blockers.append("Required CI checks not enforced")
    queue = any(
        isinstance(r, dict) and r.get("enforcement") == "active"
        and r.get("target") == "branch"
        and any(x in ("~DEFAULT_BRANCH", "~ALL", "refs/heads/main")
                for x in ((r.get("conditions") or {}).get("ref_name") or {}).get("include", []))
        and any(isinstance(rule, dict) and rule.get("type") == "merge_queue"
                for rule in r.get("rules", []))
        for r in rulesets
    )
    if not queue:
        blockers.append("No active main-scoped Merge Queue rule demonstrated")
    # A coordination ref is not a mutex when other writers may bypass it.
    blockers.append("All concurrent merge writers have not proven exclusive routing")
    return {"schema": 1, "observed_main_sha": sha,
            "eligible_for_exclusive_merge": False,
            "blockers": blockers,
            "notice": "Diagnostic only; never invoke merge API from this report."}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--branch-json", type=Path, required=True)
    p.add_argument("--rulesets-json", type=Path, required=True)
    p.add_argument("--expected-main-sha")
    a = p.parse_args()
    b = json.loads(a.branch_json.read_text(encoding="utf-8"))
    r = json.loads(a.rulesets_json.read_text(encoding="utf-8"))
    print(json.dumps(audit(b, r, a.expected_main_sha), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
