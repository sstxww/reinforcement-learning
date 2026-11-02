"""Synthetic failure-injection regressions for safe Release checkpoint installation.

No weights or simulated placement are claimed as authentic game evidence.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from tavern_ai import release_restore_entry as subject


def staged_pair(tmp_path: Path):
    staged = tmp_path / "staged"
    target = tmp_path / "checkpoint"
    staged.mkdir()
    target.mkdir()
    weights = staged / "model.zip"
    metadata = staged / "model.metadata.json"
    weights.write_bytes(b"verified-test-weights-only")
    metadata.write_text('{"schema": 1}', encoding="utf-8")
    return weights, metadata, target / "model.zip", target / "model.metadata.json"


def test_successful_install_preserves_verified_bytes(tmp_path):
    weights, metadata, target_weights, target_metadata = staged_pair(tmp_path)
    subject._install_verified_pair(weights, metadata, target_weights, target_metadata)
    assert target_weights.read_bytes() == weights.read_bytes()
    assert target_metadata.read_bytes() == metadata.read_bytes()
    assert os.path.samefile(weights, target_weights)
    assert os.path.samefile(metadata, target_metadata)


def test_preexisting_model_must_not_be_replaced(tmp_path):
    weights, metadata, target_weights, target_metadata = staged_pair(tmp_path)
    target_weights.write_bytes(b"another-session-checkpoint")
    with pytest.raises(FileExistsError):
        subject._install_verified_pair(weights, metadata, target_weights, target_metadata)
    assert target_weights.read_bytes() == b"another-session-checkpoint"
    assert not target_metadata.exists()


def test_preexisting_metadata_rolls_back_our_only_model_link(tmp_path):
    weights, metadata, target_weights, target_metadata = staged_pair(tmp_path)
    target_metadata.write_bytes(b"another-session-metadata")
    with pytest.raises(FileExistsError):
        subject._install_verified_pair(weights, metadata, target_weights, target_metadata)
    assert not target_weights.exists()
    assert target_metadata.read_bytes() == b"another-session-metadata"
    assert weights.is_file() and metadata.is_file()


def test_second_link_io_error_rolls_back(tmp_path, monkeypatch):
    weights, metadata, target_weights, target_metadata = staged_pair(tmp_path)
    real_link = os.link
    calls = []

    def fail_second(source, destination):
        calls.append(destination)
        if len(calls) == 2:
            raise PermissionError("injected I/O failure on metadata installation")
        return real_link(source, destination)

    monkeypatch.setattr(subject.os, "link", fail_second)
    with pytest.raises(PermissionError, match="injected I/O failure"):
        subject._install_verified_pair(weights, metadata, target_weights, target_metadata)
    assert len(calls) == 2
    assert not target_weights.exists()
    assert not target_metadata.exists()


def test_existing_destination_cannot_be_clobbered_after_preflight(tmp_path, monkeypatch):
    """Covers the race between original exists() precheck and install() call."""
    weights, metadata, target_weights, target_metadata = staged_pair(tmp_path)
    # A different restorer publishes its model after preflight.
    target_weights.write_bytes(b"concurrent-writer")
    with pytest.raises(FileExistsError):
        subject._install_verified_pair(weights, metadata, target_weights, target_metadata)
    assert target_weights.read_bytes() == b"concurrent-writer"


def test_failed_rollback_does_not_delete_replaced_file(tmp_path, monkeypatch):
    weights, metadata, target_weights, target_metadata = staged_pair(tmp_path)
    real_link = os.link
    calls = 0

    def racing_link(source, destination):
        nonlocal calls
        calls += 1
        if calls == 2:
            # Another process replaced the first link before metadata creation.
            target_weights.unlink()
            target_weights.write_bytes(b"new-owner-data")
            raise FileExistsError("injected raced metadata")
        return real_link(source, destination)

    monkeypatch.setattr(subject.os, "link", racing_link)
    with pytest.raises(FileExistsError):
        subject._install_verified_pair(weights, metadata, target_weights, target_metadata)
    assert target_weights.read_bytes() == b"new-owner-data"
    assert not target_metadata.exists()
