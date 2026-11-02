"""Validate provenance of a real game receipt before the PR CI replay."""
from __future__ import annotations
import json, os, re
from pathlib import Path
from tavern_ai.contract import ENGINE_HASH
from tavern_ai.validate_receipt import validate

def main():
    head = os.environ.get("GITHUB_HEAD_REF", "").strip()
    if not head:
        print("Not a PR; agent receipt requirement skipped")
        return
    parts = head.split("/")
    if len(parts) != 3 or parts[0] != "agent" or not parts[1]:
        raise SystemExit("Required branch name: agent/<agent-id>/<task>")
    agent_id = parts[1]
    candidates = sorted((Path("experiments") / agent_id).glob("*.json"))
    if not candidates:
        raise SystemExit("Missing independent agent game receipt")
    matched = 0
    for path in candidates:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate(payload)
        if payload["agent_id"] != agent_id:
            continue
        if payload.get("engine_version") != "1.1.0" or payload.get("engine_source_hash") != ENGINE_HASH:
            raise SystemExit(f"Engine provenance mismatch in {path}")
        if payload.get("policy") not in {"baseline", "model"}:
            raise SystemExit(f"Unknown policy in {path}")
        if type(payload.get("seed")) is not int or not 0 <= payload["seed"] < 2**32:
            raise SystemExit(f"Invalid seed in {path}")
        if not re.fullmatch(r"[0-9a-f]{40}", str(payload.get("git_sha", ""))):
            raise SystemExit(f"Missing source commit in {path}")
        matched += 1
    if not matched:
        raise SystemExit("Agent receipt identity mismatch")
    print(f"Validated {matched} provenance-checked full game receipts for {agent_id}")

if __name__ == "__main__":
    main()
