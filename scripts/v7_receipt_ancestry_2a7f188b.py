"""Conservative PR match receipt / source-commit ancestry audit.

An older branch game can be valid, but does not show newer code was played.
Ancestry validation is necessary, not sufficient, for real-match provenance.
This standalone auditor does not alter canonical PR acceptance rules.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

_SHA = re.compile(r"[0-9a-f]{40}\Z")


def verify_ancestry(receipt: dict, *, head: str, repo: Path) -> dict:
    """Ensure the claimed game source commit is an ancestor of the PR HEAD."""
    from tavern_ai.receipt_integrity import validate_integrity

    validate_integrity(receipt)
    source = receipt.get("git_sha")
    if not isinstance(source, str) or not _SHA.fullmatch(source):
        raise ValueError("Missing or invalid 40-hex game git_sha")
    if not isinstance(head, str) or not _SHA.fullmatch(head):
        raise ValueError("Missing or invalid 40-hex PR head")
    shallow = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--is-shallow-repository"],
        capture_output=True, text=True, check=True,
    )
    if shallow.stdout.strip() != "false":
        raise ValueError("Ancestry unverified: use a full git history")
    for candidate in (source, head):
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"{candidate}^{{commit}}"],
            check=True, capture_output=True, text=True,
        )
    relation = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", source, head],
        check=False, capture_output=True, text=True,
    )
    if relation.returncode == 1:
        raise ValueError("Game git_sha is not an ancestor of this PR head")
    if relation.returncode != 0:
        raise RuntimeError("Could not verify source commit ancestry")
    return {
        "game_git_sha": source,
        "pr_head_sha": head,
        "ancestor_verified": True,
        "authentic_game_proven": False,
        "scope": "version linkage only; inspect real Actions logs separately",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--head", required=True)
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    result = verify_ancestry(
        json.loads(args.receipt.read_text()), head=args.head, repo=args.repo,
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
