"""Bounded, engine-free negative tests for the production Artifact restore gate."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "restore_checkpoint_fail_closed.sh"


def invoke(tmp_path: Path, *, mode: str, run_id: str = "123", fresh: str = "false",
           event: str = "schedule") -> subprocess.CompletedProcess[str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True)
    gh = bin_dir / "gh"
    gh.write_text(
        "#!/usr/bin/env bash\n"
        "set -eu\n"
        "if [[ \"$1\" == api ]]; then\n"
        "  if [[ \"$MOCK_MODE\" == api_fail ]]; then exit 22; fi\n"
        "  printf '%s\\n' \"$MOCK_RUN_ID\"\n"
        "elif [[ \"$1\" == run && \"$2\" == download ]]; then\n"
        "  if [[ \"$MOCK_MODE\" == download_fail ]]; then exit 23; fi\n"
        "  mkdir -p checkpoints\n"
        "  printf 'weight data' > checkpoints/model.zip\n"
        "  if [[ \"$MOCK_MODE\" != partial ]]; then printf '{}' > checkpoints/model.metadata.json; fi\n"
        "else exit 24; fi\n",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    env = os.environ.copy()
    env.update({
        "PATH": f"{bin_dir}:{env['PATH']}",
        "GITHUB_REPOSITORY": "sstxww/reinforcement-learning",
        "GITHUB_EVENT_NAME": event,
        "FRESH_START": fresh,
        "MOCK_MODE": mode,
        "MOCK_RUN_ID": run_id,
    })
    return subprocess.run(["bash", str(SCRIPT)], cwd=tmp_path, env=env,
                          capture_output=True, text=True, check=False)


@pytest.mark.parametrize("mode,run_id", [
    ("success", ""), ("api_fail", "123"), ("download_fail", "123"),
    ("partial", "123"),
])
def test_automatic_restore_never_silently_restarts(tmp_path, mode, run_id):
    result = invoke(tmp_path, mode=mode, run_id=run_id)
    assert result.returncode != 0
    assert "refusing random reset" in result.stderr
    assert "Explicit manual fresh start" not in result.stdout


def test_valid_artifact_can_continue(tmp_path):
    result = invoke(tmp_path, mode="success")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "checkpoints/model.zip").is_file()
    assert (tmp_path / "checkpoints/model.metadata.json").is_file()


def test_manual_fresh_requires_explicit_dispatch(tmp_path):
    scheduled = invoke(tmp_path / "scheduled", mode="success", fresh="true", event="schedule")
    manual = invoke(tmp_path / "manual", mode="success", fresh="true", event="workflow_dispatch")
    assert scheduled.returncode != 0
    assert manual.returncode == 0
    assert "not checkpoint continuation" in manual.stdout
    assert not (tmp_path / "manual/checkpoints/model.zip").exists()


def test_invalid_fresh_flag_is_rejected(tmp_path):
    result = invoke(tmp_path, mode="success", fresh="maybe")
    assert result.returncode != 0
    assert "must be true or false" in result.stderr
