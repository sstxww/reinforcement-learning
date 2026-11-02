"""Require every Agent PR to include a genuine, unassisted completed game receipt.

This CI gate checks evidence admissibility, not game strength or cryptographic
authenticity. Guarded/fallback games belong in separate diagnostic reports.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from tavern_ai.receipt_integrity import validate_integrity

# Actual instrumentation uses both singular and plural guard names. Do not
# accept any of them as raw evidence, including when nested in diagnostics.
_ASSISTANCE_COUNTERS = (
    "guard_forced_end",
    "guard_forced_ends",
    "forced_end_count",
    "fallback_count",
    "fallback_actions",
    "safety_fallback_count",
)


def require_unassisted(payload: dict) -> None:
    """Reject undisclosed guard, fallback or assisted actions in a PR receipt."""
    for name in ("guarded", "assisted", "policy_fallback_used"):
        if name in payload and payload[name] is not False:
            raise ValueError(f"PR receipt is not unassisted: {name}")
    if "raw_model_only" in payload and payload["raw_model_only"] is not True:
        raise ValueError("PR receipt explicitly disclaims raw model control")

    diagnostics = payload.get("opportunity_diagnostics", {})
    if not isinstance(diagnostics, dict):
        raise ValueError("Malformed opportunity diagnostics")
    counts = diagnostics.get("counts", {})
    if not isinstance(counts, dict):
        raise ValueError("Malformed opportunity action counts")

    for origin, mapping in (("receipt", payload), ("diagnostics.counts", counts)):
        for name in _ASSISTANCE_COUNTERS:
            if name not in mapping:
                continue
            value = mapping[name]
            if type(value) is not int or value != 0:
                raise ValueError(
                    f"Assisted or malformed PR receipt counter: {origin}.{name}"
                )


def main() -> None:
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
        validate_integrity(payload)
        require_unassisted(payload)
        if payload["agent_id"] == agent_id:
            matched += 1
    if not matched:
        raise SystemExit("Agent receipt identity mismatch")
    print(f"Validated {matched} completed unassisted game receipts for {agent_id}")


if __name__ == "__main__":
    main()
