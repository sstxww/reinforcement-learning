"""Offline regression tests: no claims of actual gameplay in this file."""
import hashlib
import json
import zipfile

import pytest
from tavern_ai.model_gate_s9450775f import action_family, archive_gate


@pytest.mark.parametrize("action,expected", [
    (0, "end_turn"), (1, "refresh"), (3, "upgrade"),
    (8, "buy"), (15, "buy"), (16, "sell"), (22, "sell"),
    (2, "freeze"), (4, "hero_power"), (5, "hero_power"),
    (6, "dark_gift"), (7, "cancel"), (23, "activate"),
    (29, "activate"), (30, "choose"), (45, "choose"),
    (46, "play"), (125, "play"), (126, "magnetize"),
    (195, "magnetize"), (196, "move"), (244, "move"),
])
def test_pinned_action_bands(action, expected):
    assert action_family(action) == expected


def build_checkpoint(tmp_path, monkeypatch):
    path = tmp_path / "model.zip"
    metadata = tmp_path / "model.metadata.json"
    with zipfile.ZipFile(path, "w") as z:
        for item in ("data", "policy.pth", "policy.optimizer.pth"):
            z.writestr(item, "test")
    engine = {"version": "1.1.0", "source_hash": "hash",
              "features": 4017, "cards": 447, "actions": 245, "n_cards": 3983}
    metadata.write_text(json.dumps({"engine": engine, "total_timesteps": 128}), encoding="utf-8")
    monkeypatch.setattr("tavern_ai.model_gate_s9450775f.verify_engine", lambda: engine)
    return path, metadata, hashlib.sha256(path.read_bytes()).hexdigest()


def test_valid_archive_gate(tmp_path, monkeypatch):
    path, meta, digest = build_checkpoint(tmp_path, monkeypatch)
    result = archive_gate(path, meta, digest)
    assert result["metadata_steps"] == 128
    assert result["optimizer_present"] is True


def test_reject_hash_mismatch(tmp_path, monkeypatch):
    path, meta, digest = build_checkpoint(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        archive_gate(path, meta, "0" * 64)


def test_reject_missing_optimizer(tmp_path, monkeypatch):
    path, meta, digest = build_checkpoint(tmp_path, monkeypatch)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("data", "test")
        z.writestr("policy.pth", "test")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="optimizer"):
        archive_gate(path, meta, digest)


def test_reject_engine_drift(tmp_path, monkeypatch):
    path, meta, digest = build_checkpoint(tmp_path, monkeypatch)
    meta.write_text(json.dumps({"engine": {"version": "other"}, "total_timesteps": 128}))
    with pytest.raises(ValueError, match="incompatible"):
        archive_gate(path, meta, digest)


def test_reject_false_steps(tmp_path, monkeypatch):
    path, meta, digest = build_checkpoint(tmp_path, monkeypatch)
    m = json.loads(meta.read_text())
    m["total_timesteps"] = True
    meta.write_text(json.dumps(m))
    with pytest.raises(ValueError, match="step count"):
        archive_gate(path, meta, digest)


@pytest.mark.parametrize("invalid", [-1, 245, 246, 8.0, True, None])
def test_action_family_rejects_out_of_contract(invalid):
    with pytest.raises(ValueError, match="Illegal"):
        action_family(invalid)


def test_total_action_partition():
    from collections import Counter
    observed = Counter(action_family(action) for action in range(245))
    assert sum(observed.values()) == 245
    assert observed["buy"] == 8
    assert observed["magnetize"] == 70
    assert observed["move"] == 49
