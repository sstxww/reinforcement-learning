"""No-clobber candidate checkpoint regression; fake bytes, not a PPO result."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tavern_ai import checkpoint_writer as writer


class StubModel:
    def __init__(self, payload: bytes = b"checkpoint-test-payload"):
        self.payload = payload

    def save(self, path: str) -> None:
        Path(path).write_bytes(self.payload)


def test_fresh_versioned_candidate_installs_bound_pair(tmp_path):
    target = tmp_path / "candidate.zip"
    payload = b"first-candidate-only"
    metadata = writer.save_checkpoint(StubModel(payload), target, {"total_timesteps": 128})
    assert target.read_bytes() == payload
    assert metadata["checkpoint_sha256"] == hashlib.sha256(payload).hexdigest()
    assert writer.verify_resume_digest(target, metadata)
    assert (tmp_path / "candidate.metadata.json").is_file()
    assert not list(tmp_path.glob(".checkpoint-*"))


def test_existing_candidate_cannot_be_overwritten(tmp_path):
    target = tmp_path / "candidate.zip"
    old = writer.save_checkpoint(StubModel(b"old-protected"), target, {"step": 128})
    prior_meta = target.with_suffix(".metadata.json").read_bytes()
    with pytest.raises(FileExistsError, match="existing"):
        writer.save_checkpoint(StubModel(b"new-would-clobber"), target, {"step": 256})
    assert target.read_bytes() == b"old-protected"
    assert target.with_suffix(".metadata.json").read_bytes() == prior_meta
    assert writer.verify_resume_digest(target, old)


def test_existing_metadata_alone_is_not_overwritten(tmp_path):
    target = tmp_path / "candidate.zip"
    meta = target.with_suffix(".metadata.json")
    meta.write_bytes(b"old-metadata")
    with pytest.raises(FileExistsError):
        writer.save_checkpoint(StubModel(), target, {"step": 128})
    assert not target.exists()
    assert meta.read_bytes() == b"old-metadata"


def test_second_link_failure_rolls_back_only_new_link(tmp_path, monkeypatch):
    target = tmp_path / "candidate.zip"
    real_link = os.link
    counter = 0

    def injected_link(source, destination):
        nonlocal counter
        counter += 1
        if counter == 2:
            raise PermissionError("synthetic metadata install failure")
        return real_link(source, destination)

    monkeypatch.setattr(writer.os, "link", injected_link)
    with pytest.raises(PermissionError, match="synthetic"):
        writer.save_checkpoint(StubModel(), target, {"step": 128})
    assert counter == 2
    assert not target.exists()
    assert not target.with_suffix(".metadata.json").exists()
    assert not list(tmp_path.glob(".checkpoint-*"))


def test_new_writer_racing_after_precheck_cannot_replace_other_writer(tmp_path, monkeypatch):
    target = tmp_path / "candidate.zip"
    real_link = os.link

    def other_writer_wins(source, destination):
        if destination == target:
            target.write_bytes(b"concurrent-winner")
        return real_link(source, destination)

    monkeypatch.setattr(writer.os, "link", other_writer_wins)
    with pytest.raises(FileExistsError):
        writer.save_checkpoint(StubModel(b"loser"), target, {"step": 128})
    assert target.read_bytes() == b"concurrent-winner"
    assert not target.with_suffix(".metadata.json").exists()
    assert not list(tmp_path.glob(".checkpoint-*"))


def test_raced_replacement_not_removed_during_rollback(tmp_path, monkeypatch):
    target = tmp_path / "candidate.zip"
    real_link = os.link
    counter = 0

    def other_writer_replaces(source, destination):
        nonlocal counter
        counter += 1
        if counter == 2:
            target.unlink()
            target.write_bytes(b"other-writer-replacement")
            raise FileExistsError("synthetic raced metadata")
        return real_link(source, destination)

    monkeypatch.setattr(writer.os, "link", other_writer_replaces)
    with pytest.raises(FileExistsError):
        writer.save_checkpoint(StubModel(), target, {"step": 128})
    assert target.read_bytes() == b"other-writer-replacement"
    assert not target.with_suffix(".metadata.json").exists()
    assert not list(tmp_path.glob(".checkpoint-*"))


def test_existing_symlink_is_not_followed_or_unlinked(tmp_path):
    protected = tmp_path / "protected.dat"
    protected.write_bytes(b"do-not-touch")
    target = tmp_path / "candidate.zip"
    target.symlink_to(protected)
    with pytest.raises(FileExistsError):
        writer.save_checkpoint(StubModel(), target, {"step": 128})
    assert protected.read_bytes() == b"do-not-touch"
    assert target.is_symlink()
