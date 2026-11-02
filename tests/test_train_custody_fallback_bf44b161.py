"""Static invariants for the manual V5 Release-publish failure fallback.

These tests do not claim a GitHub Release was created or a model was trained.
"""
from pathlib import Path

WORKFLOW = (
    Path(__file__).resolve().parents[1] / ".github" / "workflows" / "train.yml"
)


def _sections():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert text.count("      - name: ") >= 5
    return text


def test_sha_bound_candidate_written_before_release_attempt():
    flow = _sections()
    digest = flow.index("name: Bind checkpoint/metadata digests before")
    release = flow.index("name: Publish immutable unpromoted candidate only after")
    assert digest < release
    digest_step = flow[digest:release]
    assert "sha256sum checkpoints/candidate.zip checkpoints/candidate.metadata.json" in digest_step
    assert "checkpoints/candidate.sha256" in digest_step


def test_publish_failure_keeps_resumable_weights_not_just_metadata():
    flow = _sections()
    last = flow.split("name: Emergency candidate custody", 1)[1]
    assert "if: always()" in last
    assert "actions/upload-artifact@v4" in last
    assert "checkpoints/candidate.zip" in last
    assert "checkpoints/candidate.metadata.json" in last
    assert "checkpoints/candidate.sha256" in last
    assert "retention-days: 90" in last
    assert "github.run_attempt" in last


def test_manual_resume_and_nonpromotion_unchanged():
    flow = _sections()
    # Continued PPO must derive from a registered Release, not silently reinitialize.
    assert "schedule:" not in flow
    assert "python -m tavern_ai.release_restore_entry" in flow
    assert "--resume checkpoints/model.zip --out checkpoints/candidate.zip" in flow
    assert "gh release create" in flow
    assert "--prerelease" in flow
    assert "Champion/Best promotion" in flow
