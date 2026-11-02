from pathlib import Path
from scripts.cleanup_temporary import clean

def test_cache_cleanup_is_dry_run_by_default(tmp_path: Path):
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "x.pyc").write_bytes(b"x")
    preserved = tmp_path / "checkpoints" / "model.zip"
    preserved.parent.mkdir()
    preserved.write_bytes(b"checkpoint")
    evidence = tmp_path / "experiments" / "game.json"
    evidence.parent.mkdir()
    evidence.write_text("{}")
    matches = clean(tmp_path)
    assert "__pycache__" in matches
    assert cache.is_dir()
    assert preserved.read_bytes() == b"checkpoint"
    clean(tmp_path, apply=True)
    assert not cache.exists()
    assert preserved.read_bytes() == b"checkpoint"
    assert evidence.read_text() == "{}"
