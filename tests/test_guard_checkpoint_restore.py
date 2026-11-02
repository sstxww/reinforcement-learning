"""Read-only synthetic artifact tests; not evidence of a real PPO restoration."""
import copy
import hashlib
import json
import zipfile

import pytest

from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES
from scripts.guard_checkpoint_restore import verify


def sample(tmp_path, schema=1):
    model = tmp_path / "model.zip"
    with zipfile.ZipFile(model, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in ("data", "policy.pth", "policy.optimizer.pth"):
            z.writestr(name, f"synthetic-{name}")
    engine = {"version": "1.1.0", "source_hash": ENGINE_HASH,
              "features": FEATURES, "cards": CARDS, "actions": ACTIONS}
    meta = {"schema": schema, "algorithm": "MaskablePPO", "engine": engine,
            "total_timesteps": 1280}
    if schema == 2:
        meta["compatibility"] = {"engine": copy.deepcopy(engine)}
    path = tmp_path / "model.metadata.json"
    path.write_text(json.dumps(meta), encoding="utf-8")
    return model, path, meta


def test_trusted_external_digest_and_optimizer_members(tmp_path):
    model, path, _ = sample(tmp_path)
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    result = verify(model, path, digest)
    assert result["sha256"] == digest and result["external_sha256_verified"]
    assert not result["optimizer_resume_tested"] and not result["model_deserialized"]


def test_valid_legacy_metadata_without_external_digest_is_not_trusted_digest(tmp_path):
    model, path, _ = sample(tmp_path, schema=2)
    assert not verify(model, path)["external_sha256_verified"]


@pytest.mark.parametrize("change", [
    lambda obj: obj.update(schema=3),
    lambda obj: obj.update(algorithm="PPO"),
    lambda obj: obj.update(total_timesteps=0),
    lambda obj: obj.update(total_timesteps=True),
    lambda obj: obj["engine"].update(actions=244),
    lambda obj: obj["engine"].update(source_hash="bad"),
])
def test_incompatible_metadata_rejected(tmp_path, change):
    model, path, meta = sample(tmp_path)
    change(meta)
    path.write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ValueError):
        verify(model, path)


def test_schema2_engine_mismatch_rejected(tmp_path):
    model, path, meta = sample(tmp_path, schema=2)
    meta["compatibility"]["engine"]["features"] = 0
    path.write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ValueError):
        verify(model, path)


def test_tampering_and_external_hash_mismatch_rejected(tmp_path):
    model, path, meta = sample(tmp_path)
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    with pytest.raises(ValueError):
        verify(model, path, "0" * 64)
    meta["checkpoint_sha256"] = digest
    path.write_text(json.dumps(meta), encoding="utf-8")
    with model.open("ab") as fh:
        fh.write(b"changed")
    with pytest.raises(ValueError):
        verify(model, path)


def test_missing_optimizer_rejected(tmp_path):
    model, path, _ = sample(tmp_path)
    with zipfile.ZipFile(model, "w") as z:
        z.writestr("policy.pth", "test")
    with pytest.raises(ValueError):
        verify(model, path)


def test_missing_file_rejected(tmp_path):
    model, path, _ = sample(tmp_path)
    path.unlink()
    with pytest.raises(FileNotFoundError):
        verify(model, path)
