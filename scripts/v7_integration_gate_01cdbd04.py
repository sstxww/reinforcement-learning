"""V7 fail-closed merge preflight. No mutations; not an exclusive lock."""
import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")

def audit(pr, checks, main_sha, expected_head, reviewed_head, ancestor):
    blockers = []
    if any(not SHA.fullmatch(x) for x in (main_sha, expected_head, reviewed_head)):
        raise ValueError("All supplied SHA values must be complete lowercase 40-hex")
    head = (pr.get("head") or {}).get("sha")
    base = pr.get("base") or {}
    if pr.get("state") != "open" or pr.get("draft") is not False:
        blockers.append("PR must be open and non-Draft")
    if base.get("ref") != "main" or base.get("sha") != main_sha:
        blockers.append("PR base != current main")
    if head != expected_head or reviewed_head != expected_head:
        blockers.append("head changed or reviewed head attestation is stale")
    if pr.get("mergeable") is not True or pr.get("mergeable_state") != "clean":
        blockers.append("GitHub mergeability not clean")
    if not ancestor:
        blockers.append("Current main is not ancestor of PR head")
    rows = checks.get("check_runs") if isinstance(checks, dict) else None
    if not isinstance(rows, list) or checks.get("total_count") != len(rows):
        blockers.append("Missing/incomplete checks (pagination unknown)")
        rows = []
    rows = [r for r in rows if isinstance(r, dict) and r.get("head_sha") == head]
    required = [r for r in rows if r.get("name") == "tests-and-full-match"]
    if not required or any(r.get("status") != "completed" or
                           r.get("conclusion") != "success" for r in required):
        blockers.append("Latest-head full-match CI unavailable/pending/failed")
    if any(r.get("status") != "completed" or r.get("conclusion") not in
           ("success", "skipped", "neutral") for r in rows):
        blockers.append("Some latest-head checks are pending/failed")
    return {"schema": 1, "pr": pr.get("number"), "main": main_sha,
            "head": head, "decision": "eligible_for_integrator" if not blockers else "blocked",
            "blockers": blockers, "exclusive_lock_proven": False,
            "postmerge_ci_passed": False, "model_promotion_authorized": False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pr", type=Path, required=True)
    p.add_argument("--checks", type=Path, required=True)
    p.add_argument("--main", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--reviewed", required=True)
    p.add_argument("--ancestor", action="store_true")
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    r = audit(json.loads(a.pr.read_text()), json.loads(a.checks.read_text()),
              a.main, a.head, a.reviewed, a.ancestor)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(r, indent=2) + "\n")
    print(json.dumps(r))
    return 0 if not r["blockers"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
