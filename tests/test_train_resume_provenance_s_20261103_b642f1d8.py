"""Offline V5 regression: a SHA-less checkpoint may never resume silently.

Fixtures are bytes only; they are NOT PPO checkpoints or real TavernGym games.
"""
import hashlib

import pytest

from tavern_ai.train import require_verified_resume


def _weights(tmp_path):
    path = tmp_path / "model.zip"
    path.write_bytes(b"synthetic-test-only-not-real-PPO")
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def test_sha_bound_checkpoint_is_accepted_as_file_integrity_only(tmp_path):
    path, digest = _weights(tmp_path)
    assert require_verified_resume(path, {"checkpoint_sha256": digest}) == digest


def test_legacy_missing_sha_never_silently_loads(tmp_path):
    path, _ = _weights(tmp_path)
    with pytest.raises(ValueError, match="SHA-less legacy PPO resume"):
        require_verified_resume(path, {"schema": 1, "total_timesteps": 1408})


def test_tampered_archive_rejected(tmp_path):
    path, digest = _weights(tmp_path)
    path.write_bytes(b"modified synthetic archive")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        require_verified_resume(path, {"checkpoint_sha256": digest})


@pytest.mark.parametrize("bad", ["", "abc", "0" * 63, "G" * 64, True, 123])
def test_invalid_sha_rejected(tmp_path, bad):
    path, _ = _weights(tmp_path)
    with pytest.raises(ValueError, match="Invalid checkpoint_sha256"):
        require_verified_resume(path, {"checkpoint_sha256": bad})


def test_missing_archive_does_not_pass(tmp_path):
    path = tmp_path / "missing.zip"
    with pytest.raises(FileNotFoundError):
        require_verified_resume(path, {"checkpoint_sha256": "a" * 64})
