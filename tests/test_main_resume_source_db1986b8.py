"""Offline registry-selection regressions. No model is downloaded or promoted."""
import copy
import json
from pathlib import Path

import pytest

from tavern_ai.main_resume_source_db1986b8 import select_source


ROOT = Path(__file__).resolve().parents[1]


def registry():
    return json.loads((ROOT / "models" / "registry.json").read_text(encoding="utf-8"))


def test_selects_only_registered_durable_unpromoted_release():
    r = select_source(registry())
    assert r["model_tag"] == "v5-s-20261102-68099929-1408-41428692617"
    assert r["expected_sha256"] == "a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632"
    assert r["source_steps"] == 1408
    assert r["role"] == "unpromoted_research_source"
    assert r["verified"] == "registry_selection_only"


@pytest.mark.parametrize("mutation", [
    lambda r: r["latest"].update(durable_storage="artifact_90days"),
    lambda r: r["latest"].update(checkpoint_sha256="0" * 64),
    lambda r: r["latest"].update(training_steps=99999),
    lambda r: r["latest"].update(model_full_game_passed=False),
    lambda r: r["latest"].update(release_tag="attacker-controlled"),
    lambda r: r["latest"].update(metadata_asset="bad.json"),
    lambda r: r["latest"].update(paired_improvement_verified=True),
    lambda r: r.update(best={"id": "unverified"}),
    lambda r: r["candidates"].append(copy.deepcopy(r["candidates"][-1])),
])
def test_rejects_missing_or_forged_resume_provenance(mutation):
    r = registry()
    mutation(r)
    with pytest.raises((ValueError, KeyError, TypeError)):
        select_source(r)


def test_cli_output_is_machine_readable(tmp_path):
    import subprocess
    import sys
    outputs = tmp_path / "outputs"
    cp = subprocess.run([
        sys.executable, "-m", "tavern_ai.main_resume_source_db1986b8",
        "--registry", str(ROOT / "models" / "registry.json"),
        "--github-output", str(outputs),
    ], cwd=ROOT, capture_output=True, text=True, check=True)
    selected = json.loads(cp.stdout)
    assert selected["source_steps"] == 1408
    lines = dict(row.split("=", 1) for row in outputs.read_text().splitlines())
    assert lines["model_tag"] == selected["model_tag"]
    assert lines["expected_sha256"] == selected["expected_sha256"]
    assert lines["source_steps"] == "1408"
