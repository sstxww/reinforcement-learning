"""Offline regression gates; synthetic ZIPs are NOT real PPO checkpoints."""
import hashlib
import json
import zipfile

import pytest

from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES
from tavern_ai.verified_resume_16ab9eb1 import (
    checked_bundle,
    resume_from_checked_release,
)

MODEL = "test-release-128"
URL = f"https://github.com/sstxww/reinforcement-learning/releases/tag/{MODEL}"


def build_case(tmp_path, *, steps=128, with_optimizer=True):
    archive = tmp_path / "model.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("data", "{}")
        z.writestr("policy.pth", b"synthetic-test-only")
        if with_optimizer:
            z.writestr("policy.optimizer.pth", b"synthetic-test-only")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    engine = {
        "version": "1.1.0", "source_hash": ENGINE_HASH,
        "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
        "n_cards": 3983,
    }
    meta = {
        "schema": 1, "engine": engine, "algorithm": "MaskablePPO",
        "total_timesteps": steps,
    }
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps(meta), encoding="utf-8")
    registry = {
        "schema": 1, "repository": "sstxww/reinforcement-learning",
        "engine": {
            "version": "1.1.0", "source_hash": ENGINE_HASH,
            "float_features": FEATURES, "card_slots": CARDS,
            "action_count": ACTIONS,
        },
        "best": None, "champion": None,
        "candidates": [{
            "id": MODEL, "role": "candidate_unpromoted",
            "release_url": URL, "checkpoint_sha256": digest, "training_steps": steps,
        }],
        "latest": {
            "id": MODEL, "release_tag": MODEL, "release": URL,
            "checkpoint_sha256": digest, "training_steps": steps,
            "model_asset": "model.zip", "metadata_asset": "model.metadata.json",
            "promoted_to_best": False,
        },
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(registry), encoding="utf-8")
    return path, archive, metadata


def test_preflight_binds_model_to_registry_steps_and_hash(tmp_path):
    r, a, m = build_case(tmp_path)
    report = checked_bundle(r, MODEL, a, m)
    assert report["archive_integrity"] == "passed"
    assert report["source_training_steps"] == 128
    assert report["model_load"] == "not_tested"
    assert report["champion_promoted"] is False


def test_corrupted_archive_is_rejected_even_if_zip_opens(tmp_path):
    r, a, m = build_case(tmp_path)
    with a.open("ab") as handle:
        handle.write(b"tamper")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        checked_bundle(r, MODEL, a, m)


def test_unknown_model_id_fails_closed(tmp_path):
    r, a, m = build_case(tmp_path)
    with pytest.raises(ValueError, match="Model ID"):
        checked_bundle(r, "not-in-catalog", a, m)


def test_training_step_metadata_must_match_registry(tmp_path):
    r, a, m = build_case(tmp_path)
    meta = json.loads(m.read_text())
    meta["total_timesteps"] += 128
    m.write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="training-step mismatch"):
        checked_bundle(r, MODEL, a, m)


def test_missing_optimizer_is_not_resumable(tmp_path):
    r, a, m = build_case(tmp_path, with_optimizer=False)
    with pytest.raises(ValueError, match="Missing PPO"):
        checked_bundle(r, MODEL, a, m)


def test_refuse_same_output_as_parent_checkpoint(tmp_path):
    r, a, m = build_case(tmp_path)
    with pytest.raises(ValueError, match="overwrite the sole source"):
        resume_from_checked_release(r, MODEL, a, m, a, 128, 1)


def test_refuse_overwrite_of_existing_child_before_training(tmp_path):
    r, a, m = build_case(tmp_path)
    out = tmp_path / "new.zip"
    out.write_bytes(b"existing-valuable-checkpoint")
    with pytest.raises(FileExistsError):
        resume_from_checked_release(r, MODEL, a, m, out, 128, 1)


def test_metadata_must_be_exact_resume_sidecar(tmp_path):
    r, a, m = build_case(tmp_path)
    other = tmp_path / "another.json"
    other.write_text(m.read_text())
    with pytest.raises(ValueError, match="exact sidecar"):
        resume_from_checked_release(r, MODEL, a, other, tmp_path / "new.zip", 128, 1)


@pytest.mark.parametrize("steps,seed", [(127, 1), (20001, 1), (128, -1), (True, 1)])
def test_training_budget_must_be_explicit_and_bounded(tmp_path, steps, seed):
    r, a, m = build_case(tmp_path)
    with pytest.raises(ValueError):
        resume_from_checked_release(r, MODEL, a, m, tmp_path / "new.zip", steps, seed)


def test_synthetic_postcondition_and_immutable_parent(tmp_path, monkeypatch):
    # Fake trainer only exercises state-transition validation; it proves NO
    # real PPO learning or full-game execution.
    r, a, m = build_case(tmp_path)
    source_before = a.read_bytes()
    def fake_train(*, steps, seed, model_out, resume):
        assert steps == 128 and seed == 9 and resume == a
        with zipfile.ZipFile(model_out, "w") as z:
            z.writestr("data", "{}")
            z.writestr("policy.pth", b"synthetic-child")
            z.writestr("policy.optimizer.pth", b"synthetic-child")
        data = json.loads(m.read_text())
        data["total_timesteps"] = 256
        model_out.with_suffix(".metadata.json").write_text(json.dumps(data))
        return data
    import tavern_ai.train as training
    monkeypatch.setattr(training, "run", fake_train)
    out = tmp_path / "child.zip"
    report = resume_from_checked_release(r, MODEL, a, m, out, 128, 9)
    assert report["actual_additional_steps"] == 128
    assert report["champion_promoted"] is False
    assert report["durable_release"] == "not_published"
    assert report["complete_match"] == "not_tested"
    assert a.read_bytes() == source_before
    assert json.loads(out.with_suffix(".lineage.json").read_text()) == report
