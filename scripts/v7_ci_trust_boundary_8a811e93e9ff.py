#!/usr/bin/env python3
"""V7 read-only trust-boundary preflight for GitHub PR full-match evidence.

This rejects PR changes to the exact files that define the existing independent
CI/game receipt gate. It is a *necessary extra check*, not proof of an
authentic game and not an exclusive main merge lease.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO = "sstxww/reinforcement-learning"
TRUSTED_EVIDENCE_PATHS = frozenset({
    ".github/workflows/ci.yml",
    ".github/workflows/v7-serialized-integrator.yml",
    "scripts/v7_serial_integrator.py",
    "scripts/check_pr_evidence.py",
    "scripts/bootstrap_engine.sh",
    "tavern_ai/canary.py",
    "tavern_ai/contract.py",
    "tavern_ai/validate_receipt.py",
    "tavern_ai/receipt_integrity.py",
    "tavern_ai/baseline.py",
    "pyproject.toml",
})


class TrustBoundaryError(RuntimeError):
    """Not enough evidence to safely treat PR CI as independently trusted."""


def exact_sha(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise TrustBoundaryError("Expected full lowercase 40-hex commit SHA")
    return value


def checked_path(value: str) -> str:
    if (not isinstance(value, str) or not value or
            "\\" in value or value.startswith("/") or
            any(component in ("", ".", "..") for component in value.split("/"))):
        raise TrustBoundaryError("Malformed PR changed path")
    return value


def audit_changed_files(files: list[dict], expected_count: int) -> dict:
    """Fail closed on incomplete pagination or modified trusted evidence code."""
    if (type(expected_count) is not int or expected_count < 1 or
            expected_count > 3000 or not isinstance(files, list) or
            len(files) != expected_count):
        raise TrustBoundaryError("Incomplete or invalid PR file-list coverage")
    changes: set[str] = set()
    filenames: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict):
            raise TrustBoundaryError("Malformed PR file record")
        status = entry.get("status")
        if status not in {
            "added", "modified", "removed", "renamed", "copied", "changed",
            "unchanged",
        }:
            raise TrustBoundaryError("Unknown PR file status")
        changed = checked_path(entry.get("filename"))
        filenames.add(changed)
        changes.add(changed)
        if status == "renamed":
            changes.add(checked_path(entry.get("previous_filename")))
    if len(filenames) != expected_count:
        raise TrustBoundaryError("Duplicate or missing PR file paths")
    forbidden = sorted(changes & TRUSTED_EVIDENCE_PATHS)
    if forbidden:
        raise TrustBoundaryError(
            "PR modifies trusted full-match CI/receipt source: " + ", ".join(forbidden)
        )
    return {"checked_files": len(files), "trusted_files_modified": 0}


class GitHubReadOnly:
    def __init__(self, token: str):
        if not token:
            raise TrustBoundaryError("Read-only GitHub API token missing")
        self.token = token

    def get(self, path: str):
        req = Request(
            "https://api.github.com/repos/" + REPO + path,
            headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "autotavern-v7-trusted-ci-audit",
            },
        )
        try:
            with urlopen(req, timeout=20) as response:
                return json.load(response)
        except (HTTPError, URLError, ValueError) as error:
            raise TrustBoundaryError(
                "GitHub read failed: " + type(error).__name__
            ) from error


def audit_pr(api: GitHubReadOnly, number: int, head_sha: str, main_sha: str) -> dict:
    """Bind all evidence to exact current main/head; no mutation or merge API."""
    if type(number) is not int or number < 1:
        raise TrustBoundaryError("Invalid PR number")
    head_sha, main_sha = exact_sha(head_sha), exact_sha(main_sha)
    if api.get("/branches/main")["commit"]["sha"] != main_sha:
        raise TrustBoundaryError("Main changed before preflight")
    pr = api.get("/pulls/" + str(number))
    if (pr.get("number") != number or pr.get("state") != "open" or
            pr.get("draft") is not False or
            (pr.get("head") or {}).get("sha") != head_sha or
            (pr.get("base") or {}).get("sha") != main_sha or
            (pr.get("base") or {}).get("ref") != "main"):
        raise TrustBoundaryError("PR identity/head/base not exact")
    files = []
    expected = pr.get("changed_files")
    if type(expected) is not int or not 1 <= expected <= 3000:
        raise TrustBoundaryError("PR changed_files outside supported range")
    for page in range(1, 32):
        batch = api.get(f"/pulls/{number}/files?per_page=100&page={page}")
        if not isinstance(batch, list) or len(batch) > 100:
            raise TrustBoundaryError("Invalid GitHub file page")
        files.extend(batch)
        if len(files) >= expected or len(batch) < 100:
            break
    result = audit_changed_files(files, expected)
    if (api.get("/branches/main")["commit"]["sha"] != main_sha or
            api.get("/pulls/" + str(number))["head"]["sha"] != head_sha):
        raise TrustBoundaryError("Main/PR changed during preflight")
    result.update({"pr": number, "main_sha": main_sha, "head_sha": head_sha,
                   "read_only": True, "authentic_match_verified": False,
                   "exclusive_merge_lease": False})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--main", required=True)
    args = parser.parse_args()
    api = GitHubReadOnly(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", ""))
    print(json.dumps(audit_pr(api, args.pr, args.head, args.main),
                     sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except TrustBoundaryError as exc:
        raise SystemExit("V7_TRUST_BOUNDARY_BLOCKED: " + str(exc))
