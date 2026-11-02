"""Synthetic YAML trigger inputs only; these are not game receipts."""
from pathlib import Path
from scripts.v7_workflow_trigger_scope_8e49e70d import _events, inspect_workflow, audit

NAME = Path(".github/workflows/experiment-s-20261103-8e49e70d.yml")


def test_scoped_push_is_not_flagged():
    yaml = """on:
  push:
    branches:
      - agent/s-20261103-8e49e70d/optimization-001
jobs:
  test:
    steps:
      - run: |
          on:
            pull_request:
"""
    assert inspect_workflow(NAME, yaml) == []
    assert "pull_request" not in _events(yaml)


def test_unfiltered_pr_even_with_base_branch_filter():
    yaml = """on:
  pull_request:
    branches: [main]
  push:
    branches: [agent/s-20261103-8e49e70d/optimization-001]
"""
    assert inspect_workflow(NAME, yaml) == ["unscoped_session_pull_request_event"]


def test_only_narrow_session_pr_paths_are_safe():
    yaml = """on:
  pull_request:
    paths:
      - scripts/scope_8e49e70d.py
      - tests/test_8e49e70d.py
"""
    assert inspect_workflow(NAME, yaml) == []
    assert inspect_workflow(NAME, yaml.replace("tests/test_8e49e70d.py", "tavern_ai/train.py")) == [
        "unscoped_session_pull_request_event"]


def test_privileged_pr_target_and_cross_repository_schedule():
    yaml = """on:
  pull_request_target:
  schedule:
    - cron: '0 0 * * *'
"""
    assert inspect_workflow(NAME, yaml) == [
        "session_pull_request_target_event", "session_cross_repository_automatic_event"]


def test_inline_unscoped_push_pr_and_non_session_file():
    yaml = "on: [push, pull_request]\n"
    assert inspect_workflow(NAME, yaml) == [
        "unscoped_session_pull_request_event", "unscoped_session_push_event"]
    assert inspect_workflow(Path(".github/workflows/ci.yml"), yaml) == []


def test_archive_summary_and_dispatch_only(tmp_path):
    root = tmp_path / ".github" / "workflows"
    root.mkdir(parents=True)
    (root / NAME.name).write_text("on:\n  workflow_dispatch:\n")
    (root / "old-s-20261103-11111111.yml").write_text("on:\n  pull_request:\n")
    (root / "ci.yml").write_text("on:\n  pull_request:\n")
    result = audit(tmp_path)
    assert result["total_workflows"] == 3
    assert result["session_workflows"] == 2
    assert result["flagged_session_workflows"] == 1
    assert result["findings"][0]["path"].endswith("old-s-20261103-11111111.yml")
