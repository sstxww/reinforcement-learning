"""Cooperative V7 task leases using atomic Git ref compare-and-swap.

TASK coordination only. Never treat a task claim as exclusive main merge authority.
Requires a Git checkout with authenticated origin; never directly writes main.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any

PREFIX = "refs/heads/claims/v7/"
HEADER = "AUTOTAVERN_TASK_CLAIM_V7\n"
TASK_RE = re.compile(r"^[a-z][a-z0-9_-]{0,39}/[a-z0-9][a-z0-9_./-]{0,79}$")
SESSION_RE = re.compile(r"^s-[0-9]{8}-[a-f0-9]{8}$")


class ClaimError(RuntimeError):
    pass


def git(*argv: str, input_text: str | None = None, ok: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(["git", *argv], text=True, input=input_text,
                       capture_output=True, check=False)
    if p.returncode not in ok:
        raise ClaimError(f"git {argv[0]} failed (exit {p.returncode}): {p.stderr.strip()[-350:]}")
    return p


def ref_for(task_key: str) -> str:
    if not TASK_RE.fullmatch(task_key) or task_key.count("/") != 1 or ".." in task_key:
        raise ClaimError("invalid canonical TASK_KEY")
    digest = hashlib.sha256(task_key.encode("utf-8")).hexdigest()[:32]
    return PREFIX + digest


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(s: str) -> datetime:
    date = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if date.tzinfo is None:
        raise ClaimError("lease timestamp has no timezone")
    return date.astimezone(timezone.utc)


def current_sha(ref: str, remote: str) -> str | None:
    res = git("ls-remote", "--refs", remote, ref)
    lines = res.stdout.strip().splitlines()
    if not lines:
        return None
    if len(lines) != 1:
        raise ClaimError("ambiguous Git task reference")
    sha, name = lines[0].split("\t", 1)
    if name != ref or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ClaimError("untrusted remote ref response")
    return sha


def read_claim(ref: str, sha: str, remote: str) -> dict[str, Any]:
    git("fetch", "--no-tags", remote, ref)
    text = git("show", "-s", "--format=%B", sha).stdout.strip()
    if not text.startswith(HEADER):
        raise ClaimError("ref is not a V7 claim; do not overwrite")
    try:
        doc = json.loads(text[len(HEADER):])
    except ValueError as exc:
        raise ClaimError("malformed V7 claim commit") from exc
    if not isinstance(doc, dict) or doc.get("version") != 1:
        raise ClaimError("unsupported V7 claim version")
    if doc.get("ref") != ref or ref_for(doc.get("task_key", "")) != ref:
        raise ClaimError("claim ref/task mismatch")
    if not SESSION_RE.fullmatch(str(doc.get("session_id", ""))):
        raise ClaimError("invalid claim owner")
    if doc.get("status") not in {"claimed", "released"}:
        raise ClaimError("invalid claim status")
    parse_time(str(doc.get("expires_at", "")))
    return doc


def make_claim_commit(doc: dict[str, Any], parent: str) -> str:
    tree = git("rev-parse", f"{parent}^{{tree}}").stdout.strip()
    message = HEADER + json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n"
    git("config", "user.name")
    git("config", "user.email")
    return git("commit-tree", tree, "-p", parent, input_text=message).stdout.strip()


def cas_push(ref: str, expected_sha: str | None, new_sha: str, remote: str) -> None:
    # Exact expected SHA, or empty if the ref must not already exist.
    p = git("push", f"--force-with-lease={ref}:{expected_sha or ''}", remote,
            f"{new_sha}:{ref}", ok=(0, 1, 128))
    if p.returncode != 0:
        raise ClaimError("atomic lease rejected: ref changed or Git denied push; re-sync and choose another task")
    if current_sha(ref, remote) != new_sha:
        raise ClaimError("post-push claim ref verification failed")


def transition(action: str, task_key: str, session_id: str, *,
               remote: str = "origin", ttl_minutes: int = 30) -> dict[str, Any]:
    ref = ref_for(task_key)
    if not SESSION_RE.fullmatch(session_id):
        raise ClaimError("invalid SESSION_ID")
    if not 5 <= ttl_minutes <= 120:
        raise ClaimError("TTL must be 5..120 minutes")
    old = current_sha(ref, remote)
    doc = read_claim(ref, old, remote) if old else None
    now = utc_now()
    if action == "inspect":
        return {"ref": ref, "sha": old, "claim": doc,
                "expired": bool(doc and parse_time(doc["expires_at"]) <= now)}
    if action == "acquire":
        if doc and doc["status"] == "claimed" and parse_time(doc["expires_at"]) > now:
            raise ClaimError(f"occupied by {doc['session_id']} until {doc['expires_at']}")
    elif action in {"renew", "release"}:
        if not doc or doc["status"] != "claimed" or doc["session_id"] != session_id:
            raise ClaimError("not the verified current task owner")
        if action == "renew" and parse_time(doc["expires_at"]) <= now:
            raise ClaimError("expired task lease cannot be renewed")
    else:
        raise ClaimError("unknown action")
    parent = old or git("rev-parse", "HEAD").stdout.strip()
    new_doc = {
        "version": 1, "ref": ref, "task_key": task_key, "session_id": session_id,
        "status": "released" if action == "release" else "claimed",
        "issued_at": now.isoformat(),
        "expires_at": (now if action == "release" else now + timedelta(minutes=ttl_minutes)).isoformat(),
        "nonce": secrets.token_hex(16),
    }
    sha = make_claim_commit(new_doc, parent)
    cas_push(ref, old, sha, remote)
    return {"ref": ref, "sha": sha, "claim": new_doc}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["acquire", "inspect", "renew", "release"])
    ap.add_argument("--task-key", required=True)
    ap.add_argument("--session-id", required=True)
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--ttl-minutes", type=int, default=30)
    a = ap.parse_args()
    try:
        print(json.dumps(transition(a.action, a.task_key, a.session_id,
                                    remote=a.remote, ttl_minutes=a.ttl_minutes), sort_keys=True))
    except ClaimError as exc:
        ap.exit(2, f"V7 task lease blocked: {exc}\n")


if __name__ == "__main__":
    main()
