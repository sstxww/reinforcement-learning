"""Fail-closed, no-network regressions for registered durable Release recovery."""
import json
from pathlib import Path
import pytest

from tavern_ai import resume_guard_5a69c4f2 as module


def valid_entry():
    tag = "v5-smoke-a1"
    return {"repository": module.REPOSITORY, "latest": {
        "id": tag, "release_tag": tag,
        "release": f"https://github.com/{module.REPOSITORY}/releases/tag/{tag}",
        "durable_storage": "github_release",
        "model_asset": "model.zip", "metadata_asset": "model.metadata.json",
        "checkpoint_sha256": "a" * 64, "training_steps": 1408,
        "release_download_sha256_verified": True, "model_load_verified": True,
        "promoted_to_best": False
    }}


@pytest.mark.parametrize("field,value", [
    ("checkpoint_sha256", "not-a-hash"),
    ("release_tag", "../bad"),
    ("durable_storage", "github_actions_artifact"),
    ("model_asset", "wrong.zip"),
    ("metadata_asset", "other.json"),
    ("training_steps", 0),
    ("release_download_sha256_verified", False),
    ("model_load_verified", False),
    ("release", "https://github.com/another/repo/releases/tag/v5-smoke-a1"),
])
def test_rejects_untrusted_or_incompatible_release(field, value):
    item = valid_entry()
    item["latest"][field] = value
    with pytest.raises(ValueError):
        module.select_release(item)


def test_no_champion_cannot_be_assumed():
    with pytest.raises(ValueError, match="No registered best"):
        module.select_release(valid_entry(), "best")


def test_refuses_wrong_repository():
    reg = valid_entry()
    reg["repository"] = "MCG-NJU/AutoTavern"
    with pytest.raises(ValueError):
        module.select_release(reg)


def test_restore_checks_integrity_before_committing_files(tmp_path, monkeypatch):
    p = tmp_path / "registry.json"
    p.write_text(json.dumps(valid_entry()))
    destination = tmp_path / "recovered"
    probes = []

    def fake_download(command, stage):
        assert command[0:3] == ["gh", "release", "download"]
        (stage / "model.zip").write_bytes(b"opaque-model")
        (stage / "model.metadata.json").write_text("{}")

    def fake_audit(archive, metadata, digest):
        assert archive.read_bytes() == b"opaque-model"
        assert digest == "a" * 64
        return {"total_timesteps": 1408, "sha256": digest, "checkpoint_metadata_schema": 2}

    monkeypatch.setattr(module, "audit_archive", fake_audit)
    monkeypatch.setattr(module, "probe_inference", lambda path: probes.append(path.name))
    report = module.restore_registered(p, destination, inference=True, downloader=fake_download)
    assert report["new_training_steps"] == 0
    assert report["promoted_to_champion"] is False
    assert (destination / "model.zip").read_bytes() == b"opaque-model"
    assert probes == ["model.zip"]
    with pytest.raises(FileExistsError):
        module.restore_registered(p, destination, downloader=fake_download)


def test_corrupt_release_does_not_overwrite_or_claim_success(tmp_path, monkeypatch):
    p = tmp_path / "registry.json"
    p.write_text(json.dumps(valid_entry()))
    destination = tmp_path / "recovered"

    def fake_download(command, stage):
        (stage / "model.zip").write_bytes(b"corrupt")
        (stage / "model.metadata.json").write_text("{}")

    def reject(*args):
        raise ValueError("Checkpoint SHA256 mismatch")

    monkeypatch.setattr(module, "audit_archive", reject)
    with pytest.raises(ValueError, match="mismatch"):
        module.restore_registered(p, destination, downloader=fake_download)
    assert not (destination / "model.zip").exists()
    assert not (destination / "source-attestation.json").exists()


def test_registry_steps_must_match_release_metadata(tmp_path, monkeypatch):
    p = tmp_path / "registry.json"
    p.write_text(json.dumps(valid_entry()))
    destination = tmp_path / "recovered"

    def fake_download(command, stage):
        (stage / "model.zip").write_bytes(b"model")
        (stage / "model.metadata.json").write_text("{}")

    monkeypatch.setattr(module, "audit_archive", lambda *args: {
        "total_timesteps": 1280, "sha256": "a" * 64, "checkpoint_metadata_schema": 2
    })
    with pytest.raises(ValueError, match="step count mismatch"):
        module.restore_registered(p, destination, downloader=fake_download)
    assert not destination.exists()
