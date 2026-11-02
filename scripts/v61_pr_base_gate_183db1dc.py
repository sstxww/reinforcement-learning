"""Read-only V6.1 P0 merge-readiness audit for stacked PRs.

A green check alone is not permission to merge. This helper reports blockers;
it never merges, labels, closes, or changes any PR.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_CHECK = "tests-and-full-match"


def audit(pr: dict, main_sha: str, checks: dict,
          *, dependencies_cleared: bool = False) -> dict:
    """Evaluate a live GitHub pull snapshot against the exact current main."""
    blockers: list[str] = []
    head = pr.get("head") or {}
    base = pr.get("base") or {}
    head_sha = head.get("sha")
    base_sha = base.get("sha")

    if not SHA.fullmatch(str(main_sha)):
        raise ValueError("Current main SHA must be a complete 40-hex digest")
    if pr.get("state") != "open":
        blockers.append("PR is not open")
    if pr.get("draft") is not False:
        blockers.append("PR is Draft or draft state is unknown")
    if base.get("ref") != "main":
        blockers.append("PR targets a non-main dependency branch")
    if base_sha != main_sha:
        blockers.append("PR base SHA differs from current main")
    if pr.get("mergeable") is not True:
        blockers.append("GitHub mergeability is false or not yet known")
    if not SHA.fullmatch(str(head_sha)):
        blockers.append("PR head SHA missing or invalid")

    items = checks.get("check_runs") if isinstance(checks, dict) else None
    if not isinstance(items, list):
        blockers.append("Latest-head CI checks are unavailable")
        items = []
    exact = [r for r in items if r.get("head_sha") == head_sha]
    required = [r for r in exact if r.get("name") == REQUIRED_CHECK]
    if not any(r.get("status") == "completed" and
               r.get("conclusion") == "success" for r in required):
        blockers.append("Required latest-head full-match CI not successful")
    if any(r.get("status") != "completed" or
           r.get("conclusion") not in ("success", "skipped", "neutral")
           for r in exact):
        blockers.append("Latest-head checks are pending or unsuccessful")
    if not dependencies_cleared:
        blockers.append("Human dependency/receipt review is not confirmed")

    return {
        "schema": 1,
        "pr_number": pr.get("number"),
        "head_sha": head_sha,
        "base_ref": base.get("ref"),
        "base_sha": base_sha,
        "audited_main_sha": main_sha,
        "required_check": REQUIRED_CHECK,
        "checked_head_runs": len(exact),
        "decision": "eligible_for_integrator_review" if not blockers else "blocked",
        "blockers": blockers,
        "auto_merge_authorized": False,
        "scope": "read_only_p0_diagnostic_not_a_merge_decision",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pr-json", type=Path, required=True)
    p.add_argument("--checks-json", type=Path, required=True)
    p.add_argument("--main-sha", required=True)
    p.add_argument("--out", type=Path)
    p.add_argument("--dependencies-cleared", action="store_true",
                   help="Integrator attests to reviewing all upstream dependencies")
    args = p.parse_args()
    pr = json.loads(args.pr_json.read_text(encoding="utf-8"))
    checks = json.loads(args.checks_json.read_text(encoding="utf-8"))
    result = audit(pr, args.main_sha, checks,
                   dependencies_cleared=args.dependencies_cleared)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n",
                            encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
