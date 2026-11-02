"""Require every Agent PR to include a real completed game receipt."""
from __future__ import annotations
import json,os
from pathlib import Path
from tavern_ai.receipt_integrity import validate_integrity

def main():
    head=os.environ.get("GITHUB_HEAD_REF","").strip()
    if not head:
        print("Not a PR; agent receipt requirement skipped")
        return
    parts=head.split("/")
    if len(parts)<3 or parts[0]!="agent" or not parts[1]:
        raise SystemExit("Required branch name: agent/<agent-id>/<task>")
    agent_id=parts[1]
    candidates=sorted((Path("experiments")/agent_id).glob("*.json"))
    if not candidates:raise SystemExit("Missing independent agent game receipt")
    matched=0
    for path in candidates:
        payload=json.loads(path.read_text(encoding="utf-8"))
        validate_integrity(payload)
        if payload["agent_id"]==agent_id:matched+=1
    if not matched:raise SystemExit("Agent receipt identity mismatch")
    print(f"Validated {matched} completed game receipts for {agent_id}")
if __name__=="__main__":main()
