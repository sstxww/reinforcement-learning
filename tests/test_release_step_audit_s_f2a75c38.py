"""Synthetic offline checks; no training, TavernGym game or Release download."""
import hashlib
import json
import sys
import types
import zipfile

import pytest

from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES
from tavern_ai.release_step_audit_s_f2a75c38 import audit, require_loaded_steps


def _case(tmp_path):
    path = tmp_path / "model.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("data", "{}")
        z.writestr("policy.pth", b"synthetic")
        z.writestr("policy.optimizer.pth", b"synthetic")
    meta = tmp_path / "model.metadata.json"
    meta.write_text(json.dumps({
        "schema": 1,
        "algorithm": "MaskablePPO",
        "total_timesteps": 128,
        "engine": {
            "version": "1.1.0", "source_hash": ENGINE_HASH,
            "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
        },
    }), encoding="utf-8")
    entry = {
        "id": "synthetic-only",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "reported_total_timesteps": 128,
    }
    return entry, path, meta


def _fake_sb3(monkeypatch, actual):
    model = types.SimpleNamespace(
        num_timesteps=actual,
        action_space=types.SimpleNamespace(n=ACTIONS),
        observation_space=types.SimpleNamespace(spaces={
            "features": types.SimpleNamespace(shape=(FEATURES,)),
            "cards": types.SimpleNamespace(shape=(CARDS,)),
        }),
    )
    fake = types.SimpleNamespace(load=lambda *args, **kwargs: model)
    monkeypatch.setitem(sys.modules, "sb3_contrib", types.SimpleNamespace(MaskablePPO=fake))


def test_read_only_loaded_steps_audit_accepts_exact_lineage(tmp_path, monkeypatch):
    entry, archive, metadata = _case(tmp_path)
    _fake_sb3(monkeypatch, 128)
    report = audit(entry, archive, metadata)
    assert report["loaded_step_lineage_verified"] is True
    assert report["optimizer_resume_verified"] is False
    assert report["competitive_gain_verified"] is False


@pytest.mark.parametrize("actual", [0, 64, 129, True, "128", None])
def test_reject_loaded_counter_drift_even_if_zip_and_metadata_match(tmp_path, monkeypatch, actual):
    entry, archive, metadata = _case(tmp_path)
    _fake_sb3(monkeypatch, actual)
    with pytest.raises(ValueError, match="Loaded SB3 num_timesteps"):
        audit(entry, archive, metadata)


def test_reject_catalog_metadata_drift_before_model_load(tmp_path, monkeypatch):
    entry, archive, metadata = _case(tmp_path)
    entry["reported_total_timesteps"] = 256
    _fake_sb3(monkeypatch, 128)
    with pytest.raises(ValueError, match="Step-count"):
        audit(entry, archive, metadata)


@pytest.mark.parametrize("actual,metadata,catalog", [(128, True, None), (128, 0, None), (128, 128, False), (128, 128, 256)])
def test_fail_closed_on_invalid_claims(actual, metadata, catalog):
    with pytest.raises(ValueError):
        require_loaded_steps(actual, metadata, catalog)
