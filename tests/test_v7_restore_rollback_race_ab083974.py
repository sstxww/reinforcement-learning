"""V7 fail-closed regression for a proposed Release install rollback (PR #175).

The production helper is not in main yet. The third test deliberately skips
until it exists; when PR #175 is integrated, it becomes a safety gate.
Synthetic file race only; no fabricated match or checkpoint claims.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from tavern_ai import release_restore_entry


def _probe_rollback_gap(installer, tmp_path: Path, monkeypatch):
    """Inject an unrelated writer after samefile() succeeds, before unlink()."""
    stage, dest = tmp_path / "stage", tmp_path / "dest"
    stage.mkdir()
    dest.mkdir()
    weight, metadata = stage / "model.zip", stage / "model.metadata.json"
    weight.write_bytes(b"source-model")
    metadata.write_bytes(b"source-metadata")
    target_weight, target_metadata = dest / "model.zip", dest / "model.metadata.json"
    original_link, original_samefile = os.link, Path.samefile
    observed = {"replaced_after_identity_check": False}

    def link_with_second_file_failure(source, target):
        if Path(target) == target_metadata:
            raise PermissionError("synthetic second-link failure")
        return original_link(source, target)

    def samefile_then_concurrent_replace(path, other):
        is_same = original_samefile(path, other)
        if is_same and Path(path) == target_weight:
            # Emulate a second writer winning *after* the identity check.
            Path(path).unlink()
            Path(path).write_bytes(b"OTHER-OWNER-CHECKPOINT")
            observed["replaced_after_identity_check"] = True
        return is_same

    with monkeypatch.context() as m:
        m.setattr(os, "link", link_with_second_file_failure)
        m.setattr(Path, "samefile", samefile_then_concurrent_replace)
        with pytest.raises(PermissionError, match="synthetic second-link failure"):
            installer(weight, metadata, target_weight, target_metadata)

    return {
        "race_injected": observed["replaced_after_identity_check"],
        "third_party_survived": target_weight.exists()
        and target_weight.read_bytes() == b"OTHER-OWNER-CHECKPOINT",
        "original_staged_intact": weight.read_bytes() == b"source-model",
    }


def _known_unsafe_identity_then_unlink(weights, metadata, target_model, target_meta):
    """Local negative control; mirrors the dangerous two-step rollback."""
    installed = []
    try:
        for source, target in ((weights, target_model), (metadata, target_meta)):
            os.link(source, target)
            installed.append((source, target))
    except BaseException:
        for source, target in reversed(installed):
            if target.samefile(source):
                target.unlink()
        raise


def _safe_failclosed_no_rollback(weights, metadata, target_model, target_meta):
    """Positive control: never delete a pathname that may belong to someone else."""
    os.link(weights, target_model)
    os.link(metadata, target_meta)


def test_probe_catches_two_step_rollback_delete(tmp_path, monkeypatch):
    result = _probe_rollback_gap(_known_unsafe_identity_then_unlink, tmp_path, monkeypatch)
    assert result == {
        "race_injected": True,
        "third_party_survived": False,
        "original_staged_intact": True,
    }


def test_failclosed_control_does_not_delete_unowned_data(tmp_path, monkeypatch):
    result = _probe_rollback_gap(_safe_failclosed_no_rollback, tmp_path, monkeypatch)
    assert result["race_injected"] is False
    assert result["original_staged_intact"] is True


def test_proposed_release_installer_does_not_unlink_new_owner(tmp_path, monkeypatch):
    installer = getattr(release_restore_entry, "_install_verified_pair", None)
    if installer is None:
        pytest.skip("PR #175 installer not yet on main; test activates on integration")
    result = _probe_rollback_gap(installer, tmp_path, monkeypatch)
    assert result["original_staged_intact"] is True
    assert not (result["race_injected"] and not result["third_party_survived"]), (
        "unsafe check-then-unlink race removed an unrelated writer's checkpoint"
    )
