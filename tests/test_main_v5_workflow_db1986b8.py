"""Static pipeline contract tests. These are not a training result."""
from pathlib import Path

def test_main_train_requires_immutable_source_and_disables_blind_weekly_runs():
    content = (Path(__file__).resolve().parents[1] / ".github/workflows/train.yml").read_text()
    for expected in ("main_resume_source_db1986b8", "checkpoint_preflight",
                     "--expected-sha256", "--probe-inference",
                     "--resume checkpoints/model.zip --out checkpoints/candidate.zip",
                     "--compare-baseline", "needs: train", "--prerelease",
                     "cmp checkpoints/candidate.zip"):
        assert expected in content
    assert "gh run download" not in content
    assert "schedule:" not in content
    assert "initializing a fresh checkpoint" not in content
    assert "if: github.ref == 'refs/heads/main'" in content
