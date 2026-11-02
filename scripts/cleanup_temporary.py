"""Dry-run-first cleanup of regenerable Python caches, not research evidence.

Integrated and tightened from draft infrastructure PR #8. Path traversal skips
model/evidence locations and symlinked directories; this is not a model GC.
"""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

CACHE_DIRS = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"})
PROTECTED_DIRS = frozenset({
    ".git", ".venv", ".tox", "vendor", "experiments", "reports", "models",
    "checkpoints", "artifacts", "research", "outputs", "runs",
})


def clean(root: Path, apply: bool = False) -> list[str]:
    """List or remove caches inside root without descending into evidence folders."""
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    targets: list[Path] = []
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current = Path(base)
        remaining: list[str] = []
        for name in dirs:
            path = current / name
            if path.is_symlink() or name in PROTECTED_DIRS:
                continue
            if name in CACHE_DIRS:
                targets.append(path)
            else:
                remaining.append(name)
        dirs[:] = remaining
        for name in files:
            path = current / name
            if not path.is_symlink() and path.suffix in {".pyc", ".pyo"}:
                targets.append(path)
    if apply:
        for path in targets:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
    return [str(path.relative_to(root)) for path in targets]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--apply", action="store_true", help="Delete caches (default: dry-run)")
    args = parser.parse_args()
    matches = clean(args.root, apply=args.apply)
    print(f"{'Removed' if args.apply else 'Would remove'} {len(matches)} regenerable cache paths")
    for path in matches[:30]:
        print(path)
    if len(matches) > 30:
        print(f"... plus {len(matches) - 30} paths")


if __name__ == "__main__":
    main()
