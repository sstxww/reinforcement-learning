"""Fail closed on dangling or unsafe receipt references in evidence summaries.

This is a reference-integrity check, not proof a game really occurred.
Original game provenance must be checked separately against Actions logs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath


class ReceiptReferenceError(ValueError):
    """A report claims an invalid or nonresolvable receipt source."""


def checked_receipts(report: Path, root: Path) -> list[Path]:
    root = root.resolve()
    report = report.resolve()
    if not report.is_relative_to(root):
        raise ReceiptReferenceError("Report must be inside repository root")
    payload = json.loads(report.read_text(encoding="utf-8"))
    refs = payload.get("original_receipts")
    if not isinstance(refs, list) or not refs:
        raise ReceiptReferenceError("Require nonempty original_receipts list")
    found: list[Path] = []
    seen: set[str] = set()
    for raw in refs:
        if not isinstance(raw, str) or not raw.strip() or "\\" in raw:
            raise ReceiptReferenceError("Invalid receipt path syntax")
        ref = PurePosixPath(raw)
        if ref.is_absolute() or ".." in ref.parts or ref.parts[0] != "experiments" or ref.suffix != ".json":
            raise ReceiptReferenceError(f"Unsafe or noncanonical receipt reference: {raw}")
        normalized = ref.as_posix()
        if normalized != raw or normalized in seen:
            raise ReceiptReferenceError(f"Duplicate or noncanonical receipt reference: {raw}")
        seen.add(normalized)
        target = (root / raw).resolve()
        if not target.is_relative_to(root / "experiments"):
            raise ReceiptReferenceError(f"Receipt escapes experiments directory: {raw}")
        if not target.is_file():
            raise ReceiptReferenceError(f"Missing referenced receipt: {raw}")
        receipt = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(receipt, dict) or receipt.get("completed") is not True:
            raise ReceiptReferenceError(f"Referenced file is not a complete game: {raw}")
        if payload.get("seed") is not None and receipt.get("seed") != payload["seed"]:
            raise ReceiptReferenceError(f"Report and receipt seeds differ: {raw}")
        found.append(target)
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    found = checked_receipts(args.report, args.root)
    print(json.dumps({"report": str(args.report), "resolved_receipts": [str(f) for f in found], "count": len(found)}, sort_keys=True))


if __name__ == "__main__":
    main()
