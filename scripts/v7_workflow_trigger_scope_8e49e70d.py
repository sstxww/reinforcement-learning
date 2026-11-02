"""Read-only budget audit for session-specific GitHub Actions triggers.

An unfiltered pull_request event on a session workflow runs for unrelated
PRs targeting main. This is a cost audit, not a merge lock.
Only parses the small top-level 'on' mapping; suspicious/unknown forms
fail closed as findings instead of being silently certified safe.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SESSION_RE = re.compile(r"s-\d{8}-[0-9a-f]{8}")
EVENT_RE = re.compile(r"\b(pull_request_target|pull_request|push|workflow_run|schedule)\b")


def _events(text: str) -> dict[str, dict[str, list[str]]]:
    """Read top-level YAML event keys; never interpret embedded run scripts."""
    events: dict[str, dict[str, list[str]]] = {}
    in_on = False
    event = None
    field = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0:
            in_on = False
            event, field = None, None
            match = re.match(r"^(?:on|['\"]on['\"]):\s*(.*)$", line)
            if match:
                in_on = True
                scalar = match.group(1).split("#", 1)[0].strip()
                if scalar:
                    for name in EVENT_RE.findall(scalar):
                        events.setdefault(name, {})
            continue
        if not in_on:
            continue
        if indent == 2:
            match = re.match(r"^([a-z_]+):(?:\s|$)", line)
            event = match.group(1) if match else None
            field = None
            if event:
                events.setdefault(event, {})
        elif indent == 4 and event:
            match = re.match(r"^([a-z_-]+):\s*(.*)$", line)
            if match:
                field = match.group(1)
                value = match.group(2).split("#", 1)[0].strip()
                if value.startswith("[") and value.endswith("]"):
                    entries = [s.strip(" '\"\t") for s in value[1:-1].split(",") if s.strip()]
                else:
                    entries = [value.strip("'\"")] if value else []
                events[event][field] = entries
            else:
                field = None
        elif indent >= 6 and event and field and line.startswith("- "):
            events[event].setdefault(field, []).append(line[2:].strip(" '\""))
    return events


def inspect_workflow(path: Path, content: str) -> list[str]:
    """Only session-owned workflow filenames are examined."""
    session = SESSION_RE.search(path.name)
    if session is None:
        return []
    short = session.group(0).rsplit("-", 1)[-1]
    events = _events(content)
    findings = []
    if not events:
        return ["unreadable_or_missing_on_event"]
    if "pull_request_target" in events:
        findings.append("session_pull_request_target_event")
    if "workflow_run" in events or "schedule" in events:
        findings.append("session_cross_repository_automatic_event")
    if "pull_request" in events:
        paths = events["pull_request"].get("paths", [])
        # PR branch filters constrain the base branch, not the session head.
        if not paths or any(short not in p and session.group(0) not in p for p in paths):
            findings.append("unscoped_session_pull_request_event")
    if "push" in events:
        branches = events["push"].get("branches", [])
        if not branches or any(not b.startswith("agent/" + session.group(0) + "/") for b in branches):
            findings.append("unscoped_session_push_event")
    return findings


def audit(root: Path) -> dict:
    paths = sorted((Path(root) / ".github" / "workflows").glob("*.y*ml"))
    rows = []
    for path in paths:
        if not SESSION_RE.search(path.name):
            continue
        findings = inspect_workflow(path, path.read_text(encoding="utf-8"))
        rows.append({"path": str(path.relative_to(root)), "findings": findings})
    return {"schema": 1, "total_workflows": len(paths),
            "session_workflows": len(rows),
            "flagged_session_workflows": sum(bool(r["findings"]) for r in rows),
            "findings": [r for r in rows if r["findings"]],
            "claim": "static trigger scope only; no actual Actions or merge authorization"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--strict", action="store_true",
                        help="nonzero when existing workflows have findings")
    args = parser.parse_args()
    result = audit(args.root)
    output = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output)
    if args.strict and result["flagged_session_workflows"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
