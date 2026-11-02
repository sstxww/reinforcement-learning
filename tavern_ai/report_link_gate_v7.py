"""Validate *committed* paths in a single-seed paired-game report.

This checks linkage and consistency of stored JSON, not whether a game truly ran.
Authenticity still requires independent GitHub Actions logs and pinned engine.
It deliberately does not change canonical gameplay or model-strength scoring.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath

from .receipt_integrity import validate_integrity

SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SESSION = re.compile(r"s-[0-9]{8}-[0-9a-f]{8}\Z")


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _committed_path(repo_root: Path, session: str, value: str) -> Path:
    if not isinstance(value, str) or "\\" in value:
        raise ValueError("Receipt link must be a repo-relative POSIX path")
    rel = PurePosixPath(value)
    if rel.is_absolute() or ".." in rel.parts or "." in rel.parts:
        raise ValueError("Unsafe receipt reference")
    if len(rel.parts) != 3 or rel.parts[:2] != ("experiments", session):
        raise ValueError("Paired original_receipts must name committed session experiments")
    if not rel.name.endswith(".json"):
        raise ValueError("Receipt link must be JSON")
    target = (repo_root / Path(*rel.parts)).resolve()
    if not target.is_relative_to(repo_root):
        raise ValueError("Receipt escaped repository root")
    if not target.is_file():
        raise ValueError(f"Committed receipt missing: {value}")
    return target


def verify_report(report_path: Path, repo_root: Path) -> dict:
    """Read-only, fail-closed cross-file check for the one-seed paired schema."""
    root = repo_root.resolve(strict=True)
    report = _load_json(report_path)
    session = report.get("session_id")
    if not isinstance(session, str) or SESSION.fullmatch(session) is None:
        raise ValueError("Invalid session ID")
    if report.get("kind") != "single_seed_descriptive_paired_real_game":
        raise ValueError("Not a supported single-seed paired report")
    seed = report.get("seed")
    seat = report.get("controlled_seat")
    if type(seed) is not int or seed < 0 or type(seat) is not int or not 0 <= seat < 8:
        raise ValueError("Invalid seed or seat")
    references = report.get("original_receipts")
    if not isinstance(references, list) or len(references) != 2 or len(set(map(str, references))) != 2:
        raise ValueError("Exactly two distinct receipt references required")
    digest = report.get("registered_model_sha256")
    if not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
        raise ValueError("Invalid registered model digest")

    ranks: dict[str, int] = {}
    for ref in references:
        receipt = _load_json(_committed_path(root, session, ref))
        validate_integrity(receipt)
        policy = receipt["policy"]
        if policy not in ("baseline", "model") or policy in ranks:
            raise ValueError("Expected one baseline and one model receipt")
        if receipt["agent_id"] != session or receipt["seed"] != seed:
            raise ValueError("Receipt session or seed differs from report")
        if type(receipt.get("seat", 0)) is not int or receipt.get("seat", 0) != seat:
            raise ValueError("Controlled seat differs from report")
        if policy == "model" and receipt["model_sha256"] != digest:
            raise ValueError("Model receipt SHA256 differs from registered digest")
        ranks[policy] = receipt["placements"][seat]
    if set(ranks) != {"baseline", "model"}:
        raise ValueError("Missing one paired arm")
    if report.get("games_completed") != 2 or report.get("sample_n_per_policy") != 1:
        raise ValueError("Report sample count disagrees with receipts")
    if (report.get("baseline_placement") != ranks["baseline"]
            or report.get("model_placement") != ranks["model"]
            or report.get("model_minus_baseline_placement")
            != ranks["model"] - ranks["baseline"]):
        raise ValueError("Report rank summary disagrees with receipts")
    return {"linked_receipts": 2, "seed": seed, "seat": seat,
            "baseline_rank": ranks["baseline"], "model_rank": ranks["model"],
            "limitations": "Static linkage only; authentic run proof must be reviewed separately"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    print(json.dumps(verify_report(args.report, args.repo_root), sort_keys=True))


if __name__ == "__main__":
    main()
