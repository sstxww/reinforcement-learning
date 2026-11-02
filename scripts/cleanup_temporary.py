"""Remove regenerable Python build caches, never experiments or checkpoint data."""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

CACHE_DIRS = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"})
PROTECTED_DIRS = frozenset({
    ".git", "vendor", "experiments", "reports", "models",
    "checkpoints", "artifacts", "research",
})

def clean(root: Path, apply: bool = False) -> list[str]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    targets: list[Path] = []
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current = Path(base)
        remaining = []
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
            if not path.is_symlink() and (name.endswith(".pyc") or name.endswith(".pyo")):
                targets.append(path)
    if apply:
        for path in targets:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
    return [str(p.relative_to(root)) for p in targets]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--apply", action="store_true", help="Actually delete caches (otherwise dry-run)")
    args = parser.parse_args()
    removed = clean(args.root, apply=args.apply)
    print(f"{'Removed' if args.apply else 'Would remove'} {len(removed)} regenerable cache paths")
    for item in removed[:30]:
        print(item)
    if len(removed) > 30:
        print(f"... plus {len(removed) - 30} paths")

if __name__ == "__main__":
    main()
