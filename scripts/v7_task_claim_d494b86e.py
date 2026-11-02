"""Single-use atomic GitHub task claim, not a main-merge lease."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

class ClaimError(RuntimeError):
    pass

class ClaimExists(ClaimError):
    pass

def claim_ref(task_key: str) -> str:
    if (not re.fullmatch(r"[a-z0-9][a-z0-9/_-]{2,127}", task_key)
            or "//" in task_key or ".." in task_key or task_key.endswith("/")):
        raise ValueError("Invalid TASK_KEY")
    return "refs/heads/claims/v7/tasks/" + hashlib.sha256(task_key.encode()).hexdigest()

def request(token: str, method: str, path: str, body=None) -> dict:
    if not token:
        raise ClaimError("GH_TOKEN or GITHUB_TOKEN required")
    req = Request("https://api.github.com/" + path,
        method=method, data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=20) as response:
            data = json.load(response)
            if not isinstance(data, dict):
                raise ClaimError("Invalid JSON response")
            return data
    except HTTPError as exc:
        if exc.code == 422 and method == "POST" and path.endswith("/git/refs"):
            raise ClaimExists("Claim already exists or rejected (HTTP 422)") from None
        raise ClaimError("GitHub HTTP " + str(exc.code)) from None
    except (URLError, TimeoutError):
        raise ClaimError("Uncertain GitHub transport outcome; inspect ref") from None

def acquire(repo: str, task_key: str, session_id: str, base_sha: str,
            token: str, api=request) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Invalid repository")
    if not re.fullmatch(r"s-[0-9]{8}-[0-9a-f]{8}", session_id):
        raise ValueError("Invalid SESSION_ID")
    if not re.fullmatch(r"[0-9a-f]{40}", base_sha):
        raise ValueError("Invalid full base SHA")
    ref = claim_ref(task_key)
    root = "repos/" + repo
    old = api(token, "GET", root + "/git/commits/" + base_sha)
    old_tree = old.get("tree", {}).get("sha")
    if not isinstance(old_tree, str) or not re.fullmatch(r"[0-9a-f]{40}", old_tree):
        raise ClaimError("Base tree unverified")
    manifest = {"schema": 1, "kind": "one_shot_task_claim_not_merge_lease",
        "session_id": session_id, "task_key": task_key, "base_main_sha": base_sha,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "reclaim": "manual_handoff_only_no_auto_takeover"}
    tree = api(token, "POST", root + "/git/trees", {"base_tree": old_tree,
        "tree": [{"path": ".task-claim-v7.json", "mode": "100644",
                  "type": "blob", "content": json.dumps(manifest, sort_keys=True) + "\n"}]})
    tree_sha = tree.get("sha")
    if not isinstance(tree_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", tree_sha):
        raise ClaimError("Claim tree unverified")
    commit = api(token, "POST", root + "/git/commits", {
        "message": "chore(v7): claim " + task_key + " for " + session_id,
        "tree": tree_sha, "parents": [base_sha]}).get("sha")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ClaimError("Claim commit unverified")
    # No GET-then-PATCH: POST new ref is the actual atomic acquisition.
    created = api(token, "POST", root + "/git/refs", {"ref": ref, "sha": commit})
    if created.get("ref") != ref or created.get("object", {}).get("sha") != commit:
        raise ClaimError("Claim create response inconsistent")
    actual = api(token, "GET", root + "/git/ref/" + quote(ref[5:], safe="/"))
    if actual.get("ref") != ref or actual.get("object", {}).get("sha") != commit:
        raise ClaimError("Claim readback inconsistent")
    return {"claimed": True, "claim_ref": ref, "owner": session_id,
            "task_key": task_key, "claim_commit": commit,
            "base_main_sha": base_sha, "merge_lease": False}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("repo", "task-key", "session-id", "base-sha"):
        parser.add_argument("--" + flag, required=True)
    args = parser.parse_args()
    try:
        result = acquire(args.repo, args.task_key, args.session_id, args.base_sha,
                         os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or "")
    except (ClaimError, ValueError) as exc:
        print(json.dumps({"claimed": False, "error": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
