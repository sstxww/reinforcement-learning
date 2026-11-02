"""V7 atomic, fail-closed task claims using Git refs and non-forced fast-forward CAS.

This is TASK isolation only, NOT an exclusive main integration lease. Every
participant must use the same deterministic task slug to gain exclusivity.
GitHub rejected/non-FF updates are failures, never silently retried.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from typing import Any, Callable

PREFIX = "autotavern-v7-task-claim:"
REPO = "sstxww/reinforcement-learning"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{2,79}$")


class ClaimError(RuntimeError):
    """A claim cannot be safely established, changed, or verified."""


class ApiError(ClaimError):
    def __init__(self, status: int, detail: str):
        self.status = status
        super().__init__(f"GitHub API {status}: {detail}")


def slug_path(slug: str) -> str:
    if not SLUG.fullmatch(slug):
        raise ClaimError("task slug must be 3..80 lowercase ascii letters/digits/hyphens")
    return "refs/heads/claims/v7/" + slug


def encode(slug: str, owner: str, nonce: str, state: str) -> str:
    if state not in ("held", "released") or not owner or not nonce:
        raise ClaimError("invalid claim metadata")
    return PREFIX + json.dumps(
        {"schema": 1, "task": slug, "owner": owner, "nonce": nonce, "state": state},
        sort_keys=True, separators=(",", ":"))


def decode(message: str, slug: str) -> dict:
    if not message.startswith(PREFIX):
        raise ClaimError("Unknown claim ref tip; refusing to treat it as available")
    try:
        record = json.loads(message[len(PREFIX):])
    except (ValueError, TypeError) as exc:
        raise ClaimError("Invalid task-claim commit metadata") from exc
    if (not isinstance(record, dict) or record.get("schema") != 1
            or record.get("task") != slug or record.get("state") not in ("held", "released")
            or not isinstance(record.get("owner"), str) or not record["owner"]
            or not isinstance(record.get("nonce"), str) or not record["nonce"]):
        raise ClaimError("Unrecognized task-claim state or task key")
    return record


def gh(method: str, path: str, payload: dict | None = None) -> dict:
    """Call GitHub CLI without passing tokens in argv or logging them."""
    if not os.environ.get("GH_TOKEN"):
        raise ClaimError("GH_TOKEN is required; no unauthenticated mutation")
    cmd = ["gh", "api", "--method", method, path]
    if payload is not None:
        cmd.extend(["--input", "-"])
    proc = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                          capture_output=True, text=True, check=False)
    if proc.returncode:
        error = proc.stderr
        code = 404 if "404" in error else (422 if "422" in error else 0)
        raise ApiError(code, "GitHub API request rejected; inspect non-sensitive CLI stderr")
    try:
        return json.loads(proc.stdout)
    except ValueError as exc:
        raise ClaimError("GitHub returned non-JSON response") from exc


def _path(repo: str, suffix: str) -> str:
    if repo != REPO:
        raise ClaimError("Only the authorized repository is writable")
    return "/repos/" + repo + "/" + suffix


def _ref(api: Callable, repo: str, slug: str) -> dict | None:
    try:
        return api("GET", _path(repo, "git/ref/heads/claims/v7/" + slug))
    except ApiError as exc:
        if exc.status == 404:
            return None
        raise


def _commit(api: Callable, repo: str, message: str, tree: str, parent: str) -> str:
    result = api("POST", _path(repo, "git/commits"), {
        "message": message, "tree": tree, "parents": [parent]})
    return result["sha"]


def ensure_claim_ref(api: Callable, repo: str, slug: str) -> None:
    """Create an unowned sentinel once. Concurrent creation loses safely."""
    slug_path(slug)
    if _ref(api, repo, slug) is not None:
        return
    main = api("GET", _path(repo, "git/ref/heads/main"))["object"]["sha"]
    tree = api("GET", _path(repo, "git/commits/" + main))["tree"]["sha"]
    initial = _commit(api, repo, encode(slug, "bootstrap", "initial", "released"), tree, main)
    try:
        api("POST", _path(repo, "git/refs"), {
            "ref": slug_path(slug), "sha": initial})
    except ApiError as exc:
        if exc.status != 422 or _ref(api, repo, slug) is None:
            raise  # only an existing ref makes racing initialization harmless


def _read(api: Callable, repo: str, slug: str) -> tuple[str, dict, str]:
    info = _ref(api, repo, slug)
    if info is None:
        raise ClaimError("Claim ref vanished")
    head = info["object"]["sha"]
    commit = api("GET", _path(repo, "git/commits/" + head))
    record = decode(commit["message"], slug)
    return head, record, commit["tree"]["sha"]


def transition(api: Callable, repo: str, slug: str, owner: str,
               nonce: str, operation: str) -> str:
    """Acquire or release with a single, non-forced divergent-commit CAS."""
    slug_path(slug)
    if not re.fullmatch(r"s-[0-9]{8}-[a-f0-9]{8,16}", owner):
        raise ClaimError("owner must be a canonical independent SESSION_ID")
    if not re.fullmatch(r"[a-f0-9]{16,64}", nonce):
        raise ClaimError("nonce must be a unique cryptographic hex token")
    if operation not in ("acquire", "release"):
        raise ClaimError("operation must be acquire or release")
    if operation == "acquire":
        ensure_claim_ref(api, repo, slug)
    head, old, tree = _read(api, repo, slug)
    if operation == "acquire":
        if old["state"] != "released":
            raise ClaimError("Task already held by another owner; do not take over")
        state = "held"
    else:
        if old["state"] != "held" or old["owner"] != owner or old["nonce"] != nonce:
            raise ClaimError("Only the exact verified owner and nonce may release")
        state = "released"
    successor = _commit(api, repo, encode(slug, owner, nonce, state), tree, head)
    try:
        api("PATCH", _path(repo, "git/refs/heads/claims/v7/" + slug),
            {"sha": successor, "force": False})
    except ApiError as exc:
        raise ClaimError("Atomic claim lost a race or ref update failed; refetch before proceeding") from exc
    checked_head, checked_record, _ = _read(api, repo, slug)
    if (checked_head != successor or checked_record["owner"] != owner
            or checked_record["nonce"] != nonce or checked_record["state"] != state):
        raise ClaimError("Post-transition claim ownership verification failed")
    return successor


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["acquire", "release"])
    parser.add_argument("--task", required=True, help="deterministic 3..80-char slug")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--nonce", required=True, help="secrets.token_hex(16), preserved for release")
    args = parser.parse_args()
    # Do not print the nonce, which is an ownership capability.
    sha = transition(gh, REPO, args.task, args.session_id, args.nonce, args.operation)
    print(json.dumps({"state": "held" if args.operation == "acquire" else "released",
                      "task": args.task, "session_id": args.session_id,
                      "verified_claim_ref_sha": sha}, sort_keys=True))


if __name__ == "__main__":
    main()
