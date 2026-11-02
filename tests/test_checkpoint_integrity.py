import hashlib
import json
import zipfile

import pytest

from tavern_ai.checkpoint_integrity import metadata_path, pinned_compatibility, save_checkpoint, verify_checkpoint

ENGINE = {"version": "1.1.0", "source_hash": "6d8712c93022ba11", "features": 4017,
          "cards": 447, "actions": 245, "n_cards": 3983}


class FakePPO:
    def __init__(self, content=b"weights"):
        self.content = content

    def save(self, path):
        with zipfile.ZipFile(path, "w") as target:
            target.writestr("policy.pth", self.content)


def sample_meta():
    return {"schema": 1, "algorithm": "MaskablePPO", "engine": ENGINE,
            "total_timesteps": 1280, "training_seed": 42}


def test_save_and_restore_with_hash(tmp_path):
    checkpoint = tmp_path / "model.zip"
    out = save_checkpoint(FakePPO(), checkpoint, sample_meta())
    assert out["checkpoint_sha256"] == hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    assert verify_checkpoint(checkpoint, ENGINE) == out
    assert metadata_path(checkpoint).name == "model.metadata.json"


def test_tamper_and_engine_mismatch_fail(tmp_path):
    path = tmp_path / "model.zip"
    save_checkpoint(FakePPO(), path, sample_meta())
    with pytest.raises(ValueError, match="engine"):
        verify_checkpoint(path, {**ENGINE, "actions": 246})
    with pytest.raises(ValueError, match="release digest"):
        verify_checkpoint(path, ENGINE, "0" * 64)
    path.write_bytes(b"bad")
    with pytest.raises(ValueError, match="SHA256"):
        verify_checkpoint(path, ENGINE)


def test_missing_hash_and_zip_corruption_fail_closed(tmp_path):
    path = tmp_path / "model.zip"
    meta = save_checkpoint(FakePPO(), path, sample_meta())
    meta.pop("checkpoint_sha256")
    metadata_path(path).write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="SHA256"):
        verify_checkpoint(path, ENGINE)
    # A hash alone is not sufficient: malformed ZIPs must also be rejected.
    path.write_bytes(b"not a zip archive")
    meta["checkpoint_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    metadata_path(path).write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="ZIP"):
        verify_checkpoint(path, ENGINE)


def test_atomic_stage_and_previous_backup(tmp_path):
    path = tmp_path / "model.zip"
    first = save_checkpoint(FakePPO(b"old"), path, sample_meta())
    previous_bytes = path.read_bytes()

    class Crash:
        def save(self, path):
            raise RuntimeError("simulated interrupted torch save")

    with pytest.raises(RuntimeError):
        save_checkpoint(Crash(), path, sample_meta())
    assert path.read_bytes() == previous_bytes
    assert verify_checkpoint(path, ENGINE) == first
    newer = save_checkpoint(FakePPO(b"new"), path, {**sample_meta(), "total_timesteps": 1408})
    assert newer["total_timesteps"] == 1408
    assert verify_checkpoint(path.with_name("model.previous.zip"), ENGINE) == first
    assert verify_checkpoint(path, ENGINE) == newer


def test_missing_pair_refuses_replace(tmp_path):
    path = tmp_path / "model.zip"
    path.write_bytes(b"only weights")
    with pytest.raises(ValueError, match="incomplete checkpoint pair"):
        save_checkpoint(FakePPO(), path, sample_meta())
    assert path.read_bytes() == b"only weights"


def test_schema2_release_fingerprint_accept_and_reject(tmp_path):
    path = tmp_path / "model.zip"
    meta = {**sample_meta(), "schema": 2, "compatibility": pinned_compatibility(ENGINE)}
    saved = save_checkpoint(FakePPO(b"v2 weights"), path, meta)
    assert saved["schema"] == 2
    assert verify_checkpoint(path, ENGINE)["compatibility"] == pinned_compatibility(ENGINE)
    saved["compatibility"]["catalog_sha256"] = "0" * 64
    metadata_path(path).write_text(json.dumps(saved))
    with pytest.raises(ValueError, match="compatibility"):
        verify_checkpoint(path, ENGINE)
