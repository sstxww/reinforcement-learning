"""R002: genuine eight-seat telemetry on two previously saved PPO checkpoints.

No retraining and no changes to shared production baseline/trainer. Every
model action, legal turn-end guard, and final placement is recorded.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import statistics

import numpy as np

from .contract import FEATURES, CARDS, ACTIONS, verify_engine
from .lr_probe_24728f13 import choose_action, SESSION, TURN_ACTION_BUDGET
from .validate_receipt import validate

SEEDS = (42174, 42175, 42176)
ORIGIN_RUN = 41416467100


def action_category(action: int) -> str:
    if action == 0:
        return "end_turn"
    if action == 3:
        return "upgrade"
    if 8 <= action < 16:
        return "buy_slot"
    if 30 <= action < 46:
        return "mandatory_choice_range"
    if 46 <= action < 126:
        return "hand_play_range"
    return "other_action"


def _json(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def real_trace(seed: int, label: str, model, sha: str, engine: dict) -> dict:
    import taverngym
    game = taverngym.Game(seed=seed)
    last_turn = -1
    used = 0
    decisions = 0
    forced = 0
    proposed_ends = 0
    max_same_action_streak = 0
    last_action = None
    same_action_streak = 0
    histogram = Counter()
    categories = Counter()
    per_turn_decisions = Counter()
    first_actions = []
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, used = turn, 0
            last_action, same_action_streak = None, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            fb, cb = game.observe2(0)
            features = np.frombuffer(fb, dtype="<f4").copy()
            cards = np.frombuffer(cb, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("TavernGym contract mismatch")
            if not np.isfinite(features).all():
                raise ValueError("Non-finite observation in real game")
            if used >= TURN_ACTION_BUDGET and mask[0]:
                action, forced_flag = choose_action(mask, None, used)
            else:
                proposed, _ = model.predict(
                    {"features": features, "cards": cards},
                    action_masks=mask, deterministic=True,
                )
                action, forced_flag = choose_action(mask, int(np.asarray(proposed).item()), used)
                if action == 0:
                    proposed_ends += 1
            if used >= 120:
                raise RuntimeError(f"Repeated-action protection exceeded: seed={seed} turn={turn}")
            if len(first_actions) < 24:
                first_actions.append(action)
            histogram[action] += 1
            categories[action_category(action)] += 1
            per_turn_decisions[str(turn)] += 1
            if action == last_action:
                same_action_streak += 1
            else:
                last_action, same_action_streak = action, 1
            max_same_action_streak = max(max_same_action_streak, same_action_streak)
            if forced_flag:
                forced += 1
            game.step(0, action)
            used += 1
            decisions += 1
        if not progressed and not game.is_over():
            raise RuntimeError(f"Game stalled: seed={seed}")
    if not game.is_over():
        raise RuntimeError(f"Full-game safety limit exceeded: seed={seed}")
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION, "arm": label, "policy": "guarded_model_action_trace",
        "seed": seed, "completed": True, "turns": int(game.turn),
        "decisions": decisions, "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end), "illegal_actions": 0,
        "guard_forced_ends": forced, "model_chosen_end_turns": proposed_ends,
        "action_histogram": {str(k): int(v) for k, v in sorted(histogram.items())},
        "action_categories": dict(sorted(categories.items())),
        "per_turn_decisions": dict(sorted(per_turn_decisions.items(), key=lambda p: int(p[0]))),
        "first_actions": first_actions,
        "max_same_action_streak": max_same_action_streak,
        "turn_budget": TURN_ACTION_BUDGET,
        "model_sha256": sha, "git_sha": os.getenv("GITHUB_SHA", ""),
    }
    validate(receipt)
    if sorted(receipt["placements"]) != list(range(1, 9)):
        raise ValueError("Eight-player placements were not a permutation")
    return receipt


def summarise(records: list[dict]) -> dict:
    if not records:
        raise ValueError("No real traces")
    for r in records:
        validate(r)
    counts = Counter()
    for r in records:
        counts.update(r["action_categories"])
    ranks = [r["placements"][0] for r in records]
    return {
        "games": len(records), "ranks": ranks,
        "mean_rank": statistics.mean(ranks),
        "top4_rate": sum(x <= 4 for x in ranks) / len(records),
        "first_rate": sum(x == 1 for x in ranks) / len(records),
        "total_actions": sum(r["decisions"] for r in records),
        "model_chosen_ends": sum(r["model_chosen_end_turns"] for r in records),
        "guard_forced_ends": sum(r["guard_forced_ends"] for r in records),
        "action_categories": dict(sorted(counts.items())),
        "max_same_action_streak": max(r["max_same_action_streak"] for r in records),
    }


def main():
    import torch
    from sb3_contrib import MaskablePPO
    torch.set_num_threads(2)
    engine = verify_engine()
    source_path = Path("reports") / SESSION / "001-lr-ablation.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source["engine"] != engine or source["run_sha"] != "ff2f28b76d6a484e248437bb27c868f3550827d1":
        raise ValueError("Wrong checkpoint provenance / engine")
    all_records = {}
    for label in ("reference", "candidate"):
        item = source["training"][label]
        p = Path(item["checkpoint_path"])
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != item["model_sha256"]:
            raise ValueError(f"Missing or altered original checkpoint: {label}")
        model = MaskablePPO.load(str(p), device="cpu")
        if int(model.num_timesteps) != 256:
            raise ValueError(f"Checkpoint training count mismatch: {label}")
        all_records[label] = []
        for seed in SEEDS:
            result = real_trace(seed, label, model, item["model_sha256"], engine)
            target = Path("experiments") / SESSION / (
                f"002-{seed}.json" if label == "candidate" else f"002-reference-{seed}.json"
            )
            _json(target, result)
            all_records[label].append(result)
            print(f"{label} seed={seed} rank={result['placements'][0]} "
                  f"model-end={result['model_chosen_end_turns']} "
                  f"forced-end={result['guard_forced_ends']} actions={result['decisions']}", flush=True)
    report = {
        "session_id": SESSION, "round": 2, "experiment_type": "engineering_action_telemetry_no_training",
        "source_checkpoint_workflow_run": ORIGIN_RUN, "source_model_sha256": {
            arm: source["training"][arm]["model_sha256"] for arm in ("reference", "candidate")
        },
        "engine": engine, "heldout_seeds": list(SEEDS),
        "summary": {label: summarise(records) for label, records in all_records.items()},
        "paired_delta_rank_candidate_minus_reference": [
            a["placements"][0] - b["placements"][0]
            for a, b in zip(all_records["candidate"], all_records["reference"])
        ],
        "interpretation": "Exploratory real-match action telemetry, not new training or a strength claim.",
    }
    report["paired_mean_delta"] = statistics.mean(report["paired_delta_rank_candidate_minus_reference"])
    _json(Path("reports") / SESSION / "002-action-telemetry.json", report)
    print(json.dumps(report["summary"], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
