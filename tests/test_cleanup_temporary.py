from pathlib import Path

import pytest

from scripts.cleanup_temporary import clean


def test_dry_run_then_remove_only_regenerable_files(tmp_path: Path):
    cache = tmp_path / "src" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "import.pyc").write_bytes(b"cache")
    orphan = tmp_path / "src" / "orphan.pyo"
    orphan.write_bytes(b"cache")
    source = tmp_path / "src" / "model.py"
    source.write_text("print('real')")
    found = clean(tmp_path)
    assert sorted(found) == ["src/__pycache__", "src/orphan.pyo"]
    assert cache.is_dir() and orphan.is_file()
    assert clean(tmp_path, apply=True) == found
    assert not cache.exists() and not orphan.exists()
    assert source.read_text() == "print('real')"


@pytest.mark.parametrize("protected", [
    ".git", ".venv", ".tox", "vendor", "experiments", "reports", "models",
    "checkpoints", "artifacts", "research", "outputs", "runs",
])
def test_protected_directory_is_never_entered(tmp_path: Path, protected: str):
    path = tmp_path / protected / "__pycache__"
    path.mkdir(parents=True)
    sentinel = path / "keep.pyc"
    sentinel.write_bytes(b"persistent")
    assert clean(tmp_path, apply=True) == []
    assert sentinel.read_bytes() == b"persistent"


def test_symlinks_are_not_traversed_or_deleted(tmp_path: Path):
    source = tmp_path / "outside"
    source.mkdir()
    (source / "__pycache__").mkdir()
    (source / "__pycache__" / "keep.pyc").write_bytes(b"data")
    root = tmp_path / "root"
    root.mkdir()
    (root / "linked").symlink_to(source, target_is_directory=True)
    (root / "file.pyc").symlink_to(source / "__pycache__" / "keep.pyc")
    assert clean(root, apply=True) == []
    assert (source / "__pycache__" / "keep.pyc").read_bytes() == b"data"


def test_invalid_root_fails_closed(tmp_path: Path):
    with pytest.raises(ValueError, match="Not a directory"):
        clean(tmp_path / "missing", apply=True)


def test_explicit_protected_root_is_rejected(tmp_path: Path):
    protected = tmp_path / "models" / "subdir"
    (protected / "__pycache__").mkdir(parents=True)
    with pytest.raises(ValueError, match="protected directory"):
        clean(protected, apply=True)
    assert (protected / "__pycache__").is_dir()
