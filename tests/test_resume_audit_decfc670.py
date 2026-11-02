from types import SimpleNamespace
import pytest

from tavern_ai.resume_audit_decfc670 import optimizer_step, resume_verified


def test_optimizer_counter_reads_actual_adam_step():
    model = SimpleNamespace(policy=SimpleNamespace(optimizer=SimpleNamespace(state={
        0: {"step": 10}, 1: {"step": 18}, 2: {"unused": 1}
    })))
    assert optimizer_step(model) == 18


def test_missing_optimizer_update_returns_zero():
    model = SimpleNamespace(policy=SimpleNamespace(optimizer=SimpleNamespace(state={})))
    assert optimizer_step(model) == 0


def test_resume_audit_rejects_unbounded_training_without_touching_model(tmp_path):
    with pytest.raises(ValueError, match="exactly 128"):
        resume_verified(tmp_path / "missing.json", tmp_path / "old.zip",
                        tmp_path / "old.metadata.json", tmp_path / "new.zip",
                        tmp_path / "report.json", steps=2048)
