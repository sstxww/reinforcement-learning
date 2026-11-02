"""Offline exact-merge-base proof for a GitHub pull_request CI workflow run.

A successful PR-HEAD run started after a main commit is NOT necessarily a
successful test of that main: its synthetic merge ref may bind an older base.
This verifier checks the run's authoritative pull_requests[].base.sha.
It is an evidence gate only, never a merge lease or a merge client.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CI_NAME = "CI - full-match gate"
CI_PATH = ".github/workflows/ci.yml"


class MergeBaseEvidenceError(ValueError):
    """A run cannot prove its exact tested head/base pairing."""


def _sha(value: str, field: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise MergeBaseEvidenceError(f"Invalid 40-hex {field}")
    return value


def verify_ci_merge_base(run: dict, *, pr_number: int, head_sha: str,
                         main_sha: str) -> dict:
    """Fail closed unless CI is green for exactly the requested PR and base.

    Even if created_at/run_started_at is after main's timestamp, the run can
    have an older bound base. No timestamps are used as a substitute for SHA.
    """
    _sha(head_sha, "PR head")
    _sha(main_sha, "main base")
    if not isinstance(pr_number, int) or isinstance(pr_number, bool) or pr_number < 1:
        raise MergeBaseEvidenceError("Invalid PR number")
    if not isinstance(run, dict):
        raise MergeBaseEvidenceError("Missing run object")
    if (run.get("event") != "pull_request"
            or run.get("name") != CI_NAME
            or str(run.get("path", "")).split("@")[0] != CI_PATH
            or run.get("status") != "completed"
            or run.get("conclusion") != "success"
            or run.get("head_sha") != head_sha):
        raise MergeBaseEvidenceError("Run is not completed successful exact-head PR CI")
    bindings = run.get("pull_requests")
    if not isinstance(bindings, list) or len(bindings) != 1 or not isinstance(bindings[0], dict):
        raise MergeBaseEvidenceError("Ambiguous/missing run-to-PR binding")
    pr = bindings[0]
    if pr.get("number") != pr_number:
        raise MergeBaseEvidenceError("Run bound to a different PR")
    head = pr.get("head")
    base = pr.get("base")
    if not isinstance(head, dict) or not isinstance(base, dict):
        raise MergeBaseEvidenceError("Missing bound PR head/base")
    if head.get("sha") != head_sha:
        raise MergeBaseEvidenceError("Run PR head binding differs")
    if base.get("ref") != "main" or base.get("sha") != main_sha:
        raise MergeBaseEvidenceError("STALE_BASE: run did not test current main")
    return {"run_id": run.get("id"), "pr_number": pr_number,
            "head_sha": head_sha, "tested_main_sha": main_sha,
            "base_bound": True, "merge_authorized": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-json", required=True, type=Path,
                        help="Unmodified GitHub GET /actions/runs/{id} JSON")
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--head", required=True)
    parser.add_argument("--main", required=True)
    args = parser.parse_args()
    payload = json.loads(args.run_json.read_text(encoding="utf-8"))
    print(json.dumps(verify_ci_merge_base(payload, pr_number=args.pr,
                                         head_sha=args.head, main_sha=args.main),
                     sort_keys=True))


if __name__ == "__main__":
    main()
