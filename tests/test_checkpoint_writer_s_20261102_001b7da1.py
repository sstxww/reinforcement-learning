"""Regression tests run without TavernGym, Torch or external network access."""
import hashlib
from pathlib import Path

import pytest

from tavern_ai.checkpoint_writer import save_checkpoint, verify_resume_digest


class StubModel:
    def __init__(self, contents=b"real-test-bytes", fail=False):
        self.contents = contents
        self.fail = fail

    def save(self, path):
        Path(path).write_bytes(self.contents[:4] if self.fail else self.contents)
        if self.fail:
            raise RuntimeError("interrupted model save")


def test_staged_save_and_checksum_bound_resume(tmp_path):
    path = tmp_path / "model.zip"
    doc = save_checkpoint(StubModel(), path, {"schema": 1, "total_timesteps": 128})
    assert doc["checkpoint_sha256"] == hashlib.sha256(b"real-test-bytes").hexdigest()
    assert verify_resume_digest(path, doc)
    assert path.read_bytes() == b"real-test-bytes"
    assert (tmp_path / "model.metadata.json").is_file()
    assert not list(tmp_path.glob(".checkpoint-*"))


def test_interrupted_save_preserves_existing_pair(tmp_path):
    path = tmp_path / "model.zip"
    old = save_checkpoint(StubModel(b"original"), path, {"schema": 1})
    with pytest.raises(RuntimeError, match="interrupted"):
        save_checkpoint(StubModel(fail=True), path, {"schema": 1})
    assert path.read_bytes() == b"original"
    assert verify_resume_digest(path, old)
    assert not list(tmp_path.glob(".checkpoint-*"))


def test_tamper_and_malformed_digest_fail_closed(tmp_path):
    path = tmp_path / "model.zip"
    doc = save_checkpoint(StubModel(), path, {"schema": 1})
    path.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="mismatch"):
        verify_resume_digest(path, doc)
    with pytest.raises(ValueError, match="Invalid"):
        verify_resume_digest(path, {"checkpoint_sha256": "garbage"})


def test_legacy_metadata_explicitly_reports_unverified(tmp_path):
    path = tmp_path / "old.zip"
    path.write_bytes(b"legacy")
    assert verify_resume_digest(path, {"schema": 1}) is False


def test_reject_ambiguous_output_path(tmp_path):
    with pytest.raises(ValueError, match=".zip"):
        save_checkpoint(StubModel(), tmp_path / "model", {})
