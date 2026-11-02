"""Static guardrails for the production incremental training workflow."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / ".github" / "workflows" / "train.yml"


def test_main_train_is_main_only_and_serialized():
    txt = TRAIN.read_text(encoding="utf-8")
    assert "if: github.ref == 'refs/heads/main'" in txt
    assert "group: tavern-ai-train-main" in txt
    assert "cancel-in-progress: false" in txt


def test_explicit_release_restore_rejects_unregistered_or_tampered_bytes():
    txt = TRAIN.read_text(encoding="utf-8")
    assert "resume_release_tag:" in txt
    assert "release_resume_gate_6ed41c9a --tag" in txt
    assert txt.count("release_resume_gate_6ed41c9a --tag") == 2
    assert '--model checkpoints/model.zip' in txt
    assert '--metadata checkpoints/model.metadata.json' in txt
    assert 'gh release download "$RESUME_RELEASE_TAG"' in txt


def test_post_eval_release_is_unpromoted_and_roundtrip_checked():
    txt = TRAIN.read_text(encoding="utf-8")
    assert "Model plays full eight-seat game" in txt
    assert "Evaluate model on held-out seeds" in txt
    assert "Publish durable unpromoted Release" in txt
    assert txt.index("Evaluate model on held-out seeds") < txt.index("Publish durable unpromoted Release")
    assert 'gh release create "$TAG"' in txt
    assert "--prerelease" in txt
    assert "cmp checkpoints/model.zip" in txt
    assert "cmp checkpoints/model.metadata.json" in txt
    assert "--probe-inference" in txt
    assert "github.repository == 'MCG-NJU/AutoTavern'" not in txt
