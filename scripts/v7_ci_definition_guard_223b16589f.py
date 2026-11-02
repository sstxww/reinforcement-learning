#!/usr/bin/env python3
"""Read-only V7 trust-boundary check for PRs that rely on the standard CI gate.

This is NOT a merge lock or a complete PR approval gate. It detects PR edits to
the very workflow/scripts whose successful step NAMES are trusted by a
downstream integrator. Gate edits require a separately controlled review/run.
"""
from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CRITICAL = frozenset({
    ".github/workflows/ci.yml",
    "scripts/check_pr_evidence.py",
    "scripts/bootstrap_engine.sh",
    "tavern_ai/canary.py",
    "tavern_ai/validate_receipt.py",
    "tavern_ai/contract.py",
    ".github/workflows/v7-serialized-integrator.yml",
    "scripts/v7_serial_integrator.py",
})
MAX_FILES = 3000
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


class GateError(RuntimeError):
    pass


def checked_path(value):
    if not isinstance(value, str) or not value or "\x00" in value:
        raise GateError("Malformed changed-file path")
    if (value.startswith("/") or "\\" in value or
            posixpath.normpath(value) != value or
            any(part in ("", ".", "..") for part in value.split("/"))):
        raise GateError("Noncanonical changed-file path")
    return value


def check_changed_files(files):
    """Reject CI trust-boundary edits, including the OLD name of a rename."""
    if not isinstance(files, list) or not files or len(files) > MAX_FILES:
        raise GateError("Incomplete or excessive changed-file evidence")
    seen = set()
    blocked = set()
    for item in files:
        if not isinstance(item, dict):
            raise GateError("Invalid GitHub changed-file record")
        current = checked_path(item.get("filename"))
        if current in seen:
            raise GateError("Duplicate changed-file record")
        seen.add(current)
        names = [current]
        if item.get("status") == "renamed":
            names.append(checked_path(item.get("previous_filename")))
        elif item.get("previous_filename") is not None:
            names.append(checked_path(item["previous_filename"]))
        blocked.update(name for name in names if name in CRITICAL)
    if blocked:
        raise GateError("CI trust-boundary files changed (require separate trusted review): "
                        + ", ".join(sorted(blocked)))
    return {"checked_files": len(files), "critical_changes": 0, "decision": "pass"}


class GitHubReadOnly:
    def __init__(self, repository, token=""):
        if not REPO_RE.fullmatch(repository):
            raise GateError("Malformed repository identity")
        self.repository = repository
        self.token = token

    def get(self, suffix):
        url = "https://api.github.com/repos/" + self.repository + suffix
        headers = {"Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28",
                   "User-Agent": "autotavern-v7-ci-trust-guard"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        try:
            with urlopen(Request(url, headers=headers), timeout=20) as stream:
                return json.load(stream)
        except (HTTPError, URLError, ValueError) as exc:
            raise GateError("Unable to read complete GitHub evidence: "
                            + type(exc).__name__) from exc


def inspect(api, pr_number, expected_head, expected_main):
    if pr_number < 1 or not SHA_RE.fullmatch(expected_head) or not SHA_RE.fullmatch(expected_main):
        raise GateError("Expected exact PR number and full SHAs")
    if api.get("/branches/main")["commit"]["sha"] != expected_main:
        raise GateError("Main changed before trust check")
    def assert_pr_identity():
        pr = api.get("/pulls/" + str(pr_number))
        if (pr.get("number") != pr_number or pr.get("state") != "open" or
                pr.get("draft") is not False or
                pr.get("base", {}).get("ref") != "main" or
                pr.get("base", {}).get("sha") != expected_main or
                pr.get("head", {}).get("sha") != expected_head or
                (pr.get("head", {}).get("repo") or {}).get("full_name") != api.repository):
            raise GateError("PR identity or exact head/main changed")
    assert_pr_identity()
    files = []
    for page in range(1, 32):
        rows = api.get("/pulls/" + str(pr_number) + "/files?per_page=100&page=" + str(page))
        if not isinstance(rows, list) or len(rows) > 100:
            raise GateError("Malformed changed-file pagination")
        files.extend(rows)
        if len(files) > MAX_FILES:
            raise GateError("More than 3000 files: incomplete API evidence")
        if len(rows) < 100:
            break
    else:
        raise GateError("Changed-file list not exhausted")
    outcome = check_changed_files(files)
    assert_pr_identity()
    if api.get("/branches/main")["commit"]["sha"] != expected_main:
        raise GateError("Main changed during trust check")
    return {"pr": pr_number, "head": expected_head, "main": expected_main, **outcome}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--head", required=True)
    parser.add_argument("--main", required=True)
    args = parser.parse_args()
    outcome = inspect(GitHubReadOnly(args.repo, os.getenv("GITHUB_TOKEN", "")),
                      args.pr, args.head, args.main)
    print(json.dumps(outcome, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except GateError as exc:
        print("V7_CI_TRUST_BOUNDARY_BLOCKED: " + str(exc), file=sys.stderr)
        sys.exit(1)
