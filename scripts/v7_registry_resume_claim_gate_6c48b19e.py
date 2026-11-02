"""Read-only provenance gate for canonical Release resume claims.

A registry flag is an assertion, not independent evidence of downloading
bytes, loading optimizer state, running PPO, or completing a model game.
This audit never downloads weights, changes Latest, or authorizes promotion.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from tavern_ai.registry_integrity import validate_registry

RELEASE_FLAGS = (
    "release_download_sha256_verified",
    "model_load_from_downloaded_release_tested",
    "independent_optimizer_resume_from_this_release_tested",
)


def audit_registry(registry: dict) -> dict:
    identity = validate_registry(registry)
    latest = registry["latest"]
    progress = registry.get("training_progress", {})
    if not isinstance(progress, dict):
        raise ValueError("Malformed historical training progress")
    claims = {}
    for key in RELEASE_FLAGS:
        value = latest.get(key)
        if value is not None and type(value) is not bool:
            raise ValueError(f"Non-boolean latest Release claim: {key}")
        claims[key] = value
    historical = progress.get("latest_release_resume_verified")
    if historical is not None and type(historical) is not bool:
        raise ValueError("Non-boolean historical resume claim")
    explicit = all(claims[key] is True for key in RELEASE_FLAGS)
    missing = [key for key in RELEASE_FLAGS if claims[key] is not True]
    ambiguous = bool(
        historical is True
        and claims["independent_optimizer_resume_from_this_release_tested"] is not True
    )
    return {
        "schema": 1,
        "repository": registry["repository"],
        "main_registry_latest_id": identity["latest_id"],
        "latest_steps": identity["latest_steps"],
        "latest_model_sha256_claim": latest["checkpoint_sha256"],
        "per_release_claims": claims,
        "historical_latest_release_resume_claim": historical,
        "historical_vs_specific_claim_requires_review": ambiguous,
        "per_release_manifest_flags_complete": explicit,
        "unmet_per_release_claims": missing,
        "checkpoint_bytes_downloaded_by_this_audit": False,
        "optimizer_state_loaded_by_this_audit": False,
        "new_ppo_steps_by_this_audit": 0,
        "new_model_games_by_this_audit": 0,
        "automatic_latest_or_champion_promotion": False,
        "release_ready_for_automatic_training_by_this_audit": False,
        "status": "manual_reverification_required",
        "explanation": (
            "Historical true flags never override a missing or false model-specific "
            "claim. Even all manifest flags set true are NOT live download, optimizer "
            "resume, real-game or merge proof. Revalidate source bytes and optimizer "
            "with an independent bounded GitHub Actions run before training."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("models/registry.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.registry.read_text(encoding="utf-8"))
    report = audit_registry(data)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
