import json
import pytest

from tavern_ai.checkpoint_registry import create_manifest, verify_manifest
from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES

COMMIT = "a" * 40


def paths(tmp_path):
    model = tmp_path / "model.zip"
    model.write_bytes(b"dummy-test-weights-only")
    metadata = tmp_path / "model.metadata.json"
    info = {"algorithm": "MaskablePPO", "total_timesteps": 256, "training_seed": 42,
            "engine": {"version": "1.1.0", "source_hash": ENGINE_HASH,
                       "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
                       "n_cards": 3984}}
    metadata.write_text(json.dumps(info), encoding="utf-8")
    return model, metadata, info


def record(tmp_path):
    model, metadata, info = paths(tmp_path)
    manifest = create_manifest(model, metadata, model_id="m-20261102-test1", source_commit=COMMIT)
    return manifest, model, metadata, info


def test_valid_manifest_is_not_promoted(tmp_path):
    entry, model, metadata, _ = record(tmp_path)
    assert verify_manifest(entry, model, metadata)["integrity"] == "passed"
    assert entry["champion_eligible"] is False
    assert entry["storage_verified"] is False
    assert entry["optimizer_resume_verified"] is False


def test_mutated_weight_rejected(tmp_path):
    entry, model, metadata, _ = record(tmp_path)
    model.write_bytes(b"mutated")
    with pytest.raises(ValueError, match="sha256 mismatch"):
        verify_manifest(entry, model, metadata)


def test_mutated_metadata_rejected(tmp_path):
    entry, model, metadata, _ = record(tmp_path)
    metadata.write_text(metadata.read_text() + " ", encoding="utf-8")
    with pytest.raises(ValueError, match="sha256 mismatch"):
        verify_manifest(entry, model, metadata)


def test_changed_steps_rejected(tmp_path):
    entry, model, metadata, info = record(tmp_path)
    entry["total_timesteps"] = 512
    with pytest.raises(ValueError, match="steps differ"):
        verify_manifest(entry, model, metadata)


def test_engine_version_mismatch_rejected(tmp_path):
    model, metadata, info = paths(tmp_path)
    info["engine"]["source_hash"] = "bad"
    metadata.write_text(json.dumps(info), encoding="utf-8")
    with pytest.raises(ValueError, match="engine"):
        create_manifest(model, metadata, model_id="m-20261102-test1", source_commit=COMMIT)


def test_invalid_algorithm_rejected(tmp_path):
    model, metadata, info = paths(tmp_path)
    info["algorithm"] = "PPO"
    metadata.write_text(json.dumps(info), encoding="utf-8")
    with pytest.raises(ValueError, match="algorithm"):
        create_manifest(model, metadata, model_id="m-20261102-test1", source_commit=COMMIT)


@pytest.mark.parametrize("role", ["Champion", "Best", "unknown"])
def test_promotion_disallowed(tmp_path, role):
    model, metadata, _ = paths(tmp_path)
    with pytest.raises(ValueError, match="Champion"):
        create_manifest(model, metadata, model_id="m-20261102-test1", source_commit=COMMIT, role=role)


def test_requires_full_commit(tmp_path):
    model, metadata, _ = paths(tmp_path)
    with pytest.raises(ValueError, match="commit"):
        create_manifest(model, metadata, model_id="m-20261102-test1", source_commit="deadbee")


def test_metadata_boolean_steps_rejected(tmp_path):
    model, metadata, info = paths(tmp_path)
    info["total_timesteps"] = True
    metadata.write_text(json.dumps(info), encoding="utf-8")
    with pytest.raises(ValueError, match="steps"):
        create_manifest(model, metadata, model_id="m-20261102-test1", source_commit=COMMIT)


def test_parent_cannot_be_self(tmp_path):
    model, metadata, _ = paths(tmp_path)
    with pytest.raises(ValueError, match="own parent"):
        create_manifest(model, metadata, model_id="m-20261102-test1",
                        parent_model_id="m-20261102-test1", source_commit=COMMIT)


def test_missing_model_rejected(tmp_path):
    model, metadata, _ = paths(tmp_path)
    model.unlink()
    with pytest.raises(FileNotFoundError):
        create_manifest(model, metadata, model_id="m-20261102-test1", source_commit=COMMIT)
