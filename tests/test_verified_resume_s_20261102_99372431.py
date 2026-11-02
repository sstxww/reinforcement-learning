"""Unit-only V5 resume gate tests. Synthetic ZIPs are NOT PPO checkpoints."""
import hashlib
import json
import zipfile

import pytest

from scripts.verified_resume_s_20261102_99372431 import (
    compatible_metadata, registry_source, resume,
)
from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES


ENGINE = {
    "version": "1.1.0", "source_hash": ENGINE_HASH,
    "features": FEATURES, "cards": CARDS, "actions": ACTIONS, "n_cards": 4096,
}


def synthetic_archive(path, label):
    with zipfile.ZipFile(path, "w") as zf:
        for name in ("data", "policy.pth", "policy.optimizer.pth"):
            zf.writestr(name, label.encode())
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(tmp_path):
    source = tmp_path / "source.zip"
    digest = synthetic_archive(source, "source-only-fixture")
    metadata = tmp_path / "source.metadata.json"
    metadata.write_text(json.dumps({
        "schema": 1, "algorithm": "MaskablePPO",
        "total_timesteps": 1408, "engine": ENGINE,
    }))
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({
        "latest": {
            "id": "fixture-release", "role": "latest_experimental_unpromoted",
            "durable_storage": "github_release", "model_asset": "model.zip",
            "metadata_asset": "model.metadata.json", "checkpoint_sha256": digest,
            "training_steps": 1408,
        },
    }))
    return source, metadata, registry, digest


def test_provenance_preserved_and_not_promoted(tmp_path, monkeypatch):
    source, metadata, registry, digest = fixture(tmp_path)
    from tavern_ai import train

    def fake_train(steps, seed, out, resume_path):
        assert steps == 128
        assert resume_path == source
        synthetic_archive(out, "new-model-only-fixture")
        return {
            "schema": 1, "algorithm": "MaskablePPO", "engine": ENGINE,
            "total_timesteps": 1536, "training_seed": seed,
        }

    monkeypatch.setattr(train, "run", fake_train)
    out = tmp_path / "candidate.zip"
    report = tmp_path / "metrics" / "result.json"
    summary = resume(registry=registry, source=source, source_metadata=metadata,
                     output=out, steps=128, seed=42, report=report)
    meta = json.loads((tmp_path / "candidate.metadata.json").read_text())
    assert meta["schema"] == 2
    assert meta["parent_sha256"] == digest
    assert meta["increment_timesteps"] == 128
    assert meta["compatibility"]["engine"] == ENGINE
    assert summary["source_preflight"] == "passed"
    assert summary["new_archive_preflight"] == "passed"
    assert summary["total_timesteps"] == 1536
    assert summary["full_match_verified"] is False
    assert summary["promotion_allowed"] is False
    assert json.loads(report.read_text()) == summary


def test_source_digest_mismatch_blocks_training(tmp_path, monkeypatch):
    source, metadata, registry, _ = fixture(tmp_path)
    data = json.loads(registry.read_text())
    data["latest"]["checkpoint_sha256"] = "0" * 64
    registry.write_text(json.dumps(data))
    from tavern_ai import train
    monkeypatch.setattr(train, "run", lambda *a, **k: pytest.fail("training must not run"))
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        resume(registry=registry, source=source, source_metadata=metadata,
               output=tmp_path / "candidate.zip", steps=128,
               seed=42, report=tmp_path / "result.json")


@pytest.mark.parametrize("updates", [
    {"total_timesteps": 1408},
    {"total_timesteps": 1535},
    {"total_timesteps": 1537},
    {"algorithm": "PPO"},
    {"engine": {"version": "tampered"}},
])
def test_incompatible_resume_output_rejected(updates):
    parent = {"total_timesteps": 1408, "engine": ENGINE}
    changed = {"total_timesteps": 1536, "engine": ENGINE, "algorithm": "MaskablePPO"}
    changed.update(updates)
    with pytest.raises(ValueError):
        compatible_metadata(parent, changed, digest="a" * 64, added_steps=128,
                            parent_id="fixture", parent_digest="b" * 64)


def test_refuses_overwrite_and_unbounded_training(tmp_path):
    source, metadata, registry, _ = fixture(tmp_path)
    with pytest.raises(ValueError, match="128"):
        resume(registry=registry, source=source, source_metadata=metadata,
               output=tmp_path / "candidate.zip", steps=2048, seed=42,
               report=tmp_path / "result.json")
    with pytest.raises(ValueError, match="overwrite"):
        resume(registry=registry, source=source, source_metadata=metadata,
               output=source, steps=128, seed=42, report=tmp_path / "result.json")


def test_registry_never_assumes_champion(tmp_path):
    _, _, registry, _ = fixture(tmp_path)
    assert registry_source(registry)["role"] == "latest_experimental_unpromoted"
    data = json.loads(registry.read_text())
    data["latest"]["role"] = "champion"
    registry.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="role"):
        registry_source(registry)
