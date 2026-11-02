"""Offline workflow permission regression; not evidence of a PPO training run."""
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/train.yml"


def sections():
    text = WORKFLOW.read_text(encoding="utf-8")
    train, sep, publish = text.partition("\n  publish:\n")
    assert sep, "The Release publisher must be a separate job"
    return train, publish


def test_training_and_engine_dependencies_remain_read_only():
    train, publish = sections()
    assert "permissions:\n  contents: read\n" in train
    assert "permissions:\n  contents: write" not in train
    assert "\n    env:\n      GH_TOKEN:" not in train
    assert "GH_TOKEN:" in train
    assert "gh release create" not in train
    assert "permissions:\n      contents: write\n" in publish
    assert "needs: train" in publish
    assert "gh release create" in publish


def test_release_requires_integrity_and_model_evidence():
    train, publish = sections()
    assert "python -m tavern_ai.release_restore_entry" in train
    assert "--resume checkpoints/model.zip" in train
    assert "--compare-baseline" in train
    assert "python -m tavern_ai.validate_receipt" in train
    assert "python -m tavern_ai.checkpoint_preflight" in train
    assert "candidate_steps" in train and "parent_steps" in train
    assert "sha256sum -c checksums.sha256" in publish
    assert "model_evidence_mode" in publish
    assert "cmp publish/model.zip verification/model.zip" in publish
    assert "champion_promoted == false" in publish
