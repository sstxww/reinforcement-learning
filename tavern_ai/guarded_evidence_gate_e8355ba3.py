"""Fail-closed reconciliation of authentic raw-loop and guarded-game evidence.

This does not run a model, certify a checkpoint, or claim a strength gain.
It prevents an incomplete raw PPO trace from being counted as a completed
game and prevents a guarded game from being reported as raw-policy success.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ENGINE = "6d8712c93022ba11"


def audit(raw: dict, paired: dict) -> dict:
    if raw.get("schema") != 1 or paired.get("schema") != 1:
        raise ValueError("Unsupported evidence schema")
    if raw.get("source_model_sha256") != paired.get("model_sha256"):
        raise ValueError("Evidence is not for the same source model")
    if paired.get("engine_source_hash") != ENGINE:
        raise ValueError("Unpinned TavernGym source")
    if raw.get("complete_eight_seat_game") is not False or raw.get("final_controlled_placement") is not None:
        raise ValueError("Raw bounded trace must remain explicitly incomplete")
    if raw.get("model_controlled") is not True or raw.get("safety_fallback_count") != 0:
        raise ValueError("Raw trace cannot contain fallback decisions")
    if raw.get("failure_reason") != "model_failed_to_finish_before_bounded_iteration_limit":
        raise ValueError("Raw noncompletion evidence is missing")
    decisions = raw.get("decisions")
    counts = raw.get("action_families")
    if type(decisions) is not int or decisions <= 0 or not isinstance(counts, dict):
        raise ValueError("Malformed decision counters")
    if any(type(n) is not int or n < 0 for n in counts.values()) or sum(counts.values()) != decisions:
        raise ValueError("Raw action families do not reconcile with decision count")
    opportunities, buys = raw.get("buy_legal_decisions"), raw.get("actual_buys")
    if (type(opportunities) is not int or type(buys) is not int
            or not 0 <= buys <= opportunities <= decisions):
        raise ValueError("Malformed raw BUY opportunity counters")

    guarded = paired.get("guarded_model")
    baseline = paired.get("baseline")
    if not isinstance(guarded, dict) or not isinstance(baseline, dict):
        raise ValueError("Paired comparison must keep guarded and baseline separate")
    seeds = guarded.get("seeds")
    if not isinstance(seeds, list) or not seeds or len(seeds) != len(set(seeds)):
        raise ValueError("Missing or duplicate evaluation seeds")
    if seeds != baseline.get("seeds"):
        raise ValueError("Unpaired evaluation seeds")
    required = ("ranks", "decisions", "guard_interventions", "buys", "legal_buy_turns", "completed")
    if any(not isinstance(guarded.get(k), list) or len(guarded[k]) != len(seeds) for k in required):
        raise ValueError("Incomplete guarded game telemetry")
    if not isinstance(baseline.get("ranks"), list) or len(baseline["ranks"]) != len(seeds):
        raise ValueError("Incomplete baseline rank telemetry")
    if not all(x is True for x in guarded["completed"]):
        raise ValueError("Cannot count an incomplete guarded game")
    if any(type(x) is not int or not 1 <= x <= 8 for x in guarded["ranks"] + baseline["ranks"]):
        raise ValueError("Invalid completed-game rank")
    for n, interventions, purchases, opportunities_turns in zip(
            guarded["decisions"], guarded["guard_interventions"],
            guarded["buys"], guarded["legal_buy_turns"]):
        if (any(type(x) is not int for x in (n, interventions, purchases, opportunities_turns))
                or not 0 <= interventions <= n or not 0 <= purchases <= n
                or not 0 <= opportunities_turns <= n):
            raise ValueError("Invalid guarded telemetry counters")
    deltas = [a - b for a, b in zip(guarded["ranks"], baseline["ranks"])]
    if deltas != paired.get("paired_deltas"):
        raise ValueError("Inconsistent paired rank deltas")
    if paired.get("champion_eligible") is not False:
        raise ValueError("This evidence must not promote Champion")
    return {
        "source_model_sha256": raw["source_model_sha256"],
        "raw_model_completed": False,
        "raw_decisions": decisions,
        "raw_hero_power_cancel_actions": counts.get("hero_power", 0) + counts.get("cancel", 0),
        "raw_buy_legal_decisions": opportunities,
        "raw_buys": buys,
        "raw_game_rank": None,
        "guarded_games_completed": len(seeds),
        "guard_interventions": sum(guarded["guard_interventions"]),
        "guarded_buys": sum(guarded["buys"]),
        "guarded_ranks": guarded["ranks"],
        "paired_baseline_ranks": baseline["ranks"],
        "paired_mean_rank_delta": sum(deltas) / len(deltas),
        "model_training_steps_this_audit": 0,
        "champion_promotable": False,
        "interpretation": "Raw model noncompletion and guarded eighth-place results are different evidence classes; legal BUY does not establish optimal purchase.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--guarded", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = audit(json.loads(args.raw.read_text(encoding="utf-8")),
                   json.loads(args.guarded.read_text(encoding="utf-8")))
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
