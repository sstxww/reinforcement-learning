"""Require valid pinned-engine complete-game evidence in every Agent PR.

Canonical baseline/model receipts use the existing strict integrity validator.
Other *explicitly labelled* experimental policies (e.g. model_guarded) receive
the same game/engine/seed integrity checks, without mislabelling those games
as an unguarded PPO model. Structural checks never prove real execution;
independent workflow evidence is required separately.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from tavern_ai.contract import ENGINE_HASH
from tavern_ai.receipt_integrity import validate_integrity
from tavern_ai.validate_receipt import validate as validate_legacy

_SHA256 = re.compile(r"[a-f0-9]{64}")


def validate_pr_receipt(payload: dict) -> None:
    """Reject forged/incompatible evidence without breaking guarded-study labels."""
    validate_legacy(payload)
    if sorted(payload["placements"]) != list(range(1, 9)):
        raise ValueError("Eight placements must be a permutation of 1..8")
    if type(payload.get("seed")) is not int or payload["seed"] < 0:
        raise ValueError("Missing or invalid integer game seed")
    if payload.get("engine_version") != "1.1.0" or payload.get("engine_source_hash") != ENGINE_HASH:
        raise ValueError("Incompatible pinned TavernGym engine")
    if type(payload.get("truncated_combats")) is not int or type(payload.get("turn_limit_end")) is not bool:
        raise ValueError("Simulator truncation fields require explicit types")
    policy = payload.get("policy")
    if policy in ("baseline", "model"):
        validate_integrity(payload)
        return
    if not isinstance(policy, str) or not policy.strip():
        raise ValueError("Experimental receipts require an explicit policy label")
    digest = payload.get("model_sha256")
    if digest is not None and (not isinstance(digest, str) or not _SHA256.fullmatch(digest)):
        raise ValueError("Invalid experimental model checkpoint digest")
    if "model" in policy.lower() and (not isinstance(digest, str) or not _SHA256.fullmatch(digest)):
        raise ValueError("Model-derived experimental receipt must identify checkpoint SHA256")
    # This is still evidence of a completed game only, never evidence of
    # an unguarded model, policy gain, optimizer resume or Champion eligibility.


def main():
    head = os.environ.get("GITHUB_HEAD_REF", "").strip()
    if not head:
        print("Not a PR; agent receipt requirement skipped")
        return
    parts = head.split("/")
    if len(parts) < 3 or parts[0] != "agent" or not parts[1]:
        raise SystemExit("Required branch name: agent/<agent-id>/<task>")
    agent_id = parts[1]
    candidates = sorted((Path("experiments") / agent_id).glob("*.json"))
    if not candidates:
        raise SystemExit("Missing independent agent game receipt")
    matched = 0
    for path in candidates:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_pr_receipt(payload)
        if payload["agent_id"] == agent_id:
            matched += 1
    if not matched:
        raise SystemExit("Agent receipt identity mismatch")
    print(f"Validated {matched} pinned-engine completed game receipts for {agent_id}; guarded results remain diagnostic-only")


if __name__ == "__main__":
    main()
