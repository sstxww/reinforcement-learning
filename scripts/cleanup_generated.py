"""Conservative post-run cleanup: caches ONLY. Valuable models/data never deleted.

Default is dry-run. Use --apply only after training evidence is secured.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil

CACHE_DIRS = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"})
PROTECTED = frozenset({".git", "vendor", "models", "checkpoints",
                        "experiments", "reports", "artifacts", "runs", "outputs"})

def candidates(root: Path) -> list[Path]:
    root = root.resolve()
    found = []
    def visit(directory: Path) -> None:
        for path in directory.iterdir():
            if path.is_symlink():
                continue
            if path.is_dir():
                if path.name in CACHE_DIRS:
                    found.append(path)
                elif path.name not in PROTECTED:
                    visit(path)
            elif path.suffix in {".pyc", ".pyo"}:
                found.append(path)
    visit(root)
    return sorted(found)

def clean(root: Path, apply: bool = False) -> list[Path]:
    found = candidates(root)
    if apply:
        for path in found:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    return found

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--apply", action="store_true", help="Delete only safe caches")
    a = p.parse_args()
    for path in clean(a.root, a.apply):
        print(("REMOVED" if a.apply else "WOULD REMOVE"), path)
    print("Never touches checkpoints, experiment receipts, reports or model registry.")

if __name__ == "__main__":
    main()
