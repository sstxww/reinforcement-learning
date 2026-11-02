"""Session-local real TavernGym freeze-at-exit ablation; never uses a fake engine."""
from __future__ import annotations

import hashlib
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from tavern_ai.baseline import BaselinePolicy
from tavern_ai.contract import ACTIONS, CARDS, FEATURES, verify_engine
from tavern_ai.validate_receipt import validate

SESSION_ID = "s-20261102-717d0e50"
SEEDS = tuple(range(29101, 29111))
MAX_LOOPS = 30_000
FREEZE_TURNS = range(4, 10)
BASE = BaselinePolicy()


def select_action(mask: np.ndarray, turn: int, actions_used: int, froze_this_turn: bool, candidate: bool) -> int:
    """Apply a single legal Freeze instead of EndTurn when out of economic options."""
    action = BASE.act({"action_mask": mask}, {"turn": turn, "actions_used": actions_used})
    if (
        candidate and action == 0 and not froze_this_turn and actions_used < 85
        and turn in FREEZE_TURNS and mask[2] and not mask[1]
        and not mask[8:16].any()
    ):
        return 2
    return action


def full_match(seed: int, candidate: bool, engine: dict) -> dict:
    import taverngym

    game = taverngym.Game(seed=seed)
    decisions = 0
    freeze_actions = 0
    actions_this_turn = 0
    last_turn = -1
    froze_this_turn = False
    for _ in range(MAX_LOOPS):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn = turn
            actions_this_turn = 0
            froze_this_turn = False
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            feature_bytes, card_bytes = game.observe2(0)
            features = np.frombuffer(feature_bytes, dtype="<f4")
            cards = np.frombuffer(card_bytes, dtype="<i4")
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned observe2 contract mismatch")
            if not np.isfinite(features).all() or not mask.any():
                raise ValueError("Invalid observation values or empty action mask")
            action = select_action(mask, turn, actions_this_turn, froze_this_turn, candidate)
            if not mask[action]:
                raise ValueError(f"Illegal action {action}, seed={seed}, turn={turn}")
            game.step(0, action)
            decisions += 1
            actions_this_turn += 1
            if action == 2:
                freeze_actions += 1
                froze_this_turn = True
        if not progress and not game.is_over():
            raise RuntimeError(f"Game stalled at seed {seed} turn {turn}")
    if not game.is_over():
        raise RuntimeError(f"Full-game safety limit exceeded: seed={seed}, candidate={candidate}")
    record = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION_ID,
        "policy": "freeze-at-exit" if candidate else "baseline",
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "model_sha256": None,
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "freeze_actions": freeze_actions,
        "illegal_actions": 0,
        "action_cap": 85,
    }
    validate(record)
    if record["illegal_actions"] or record["turn_limit_end"] or record["truncated_combats"]:
        raise ValueError("Engine or legality guard failed")
    return record


def describe(records: list[dict]) -> dict:
    ranks = [r["placements"][0] for r in records]
    return {
        "games": len(records),
        "mean_rank": statistics.mean(ranks),
        "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
        "first_place_rate": sum(x == 1 for x in ranks) / len(ranks),
        "ranks": ranks,
        "freeze_actions": sum(r["freeze_actions"] for r in records),
        "decisions": sum(r["decisions"] for r in records),
    }


def main() -> None:
    engine = verify_engine()
    folder = Path("experiments") / SESSION_ID
    folder.mkdir(parents=True, exist_ok=True)
    candidate_records = []
    control_records = []
    for seed in SEEDS:
        control = full_match(seed, False, engine)
        candidate = full_match(seed, True, engine)
        for name, record in (
            (f"control-{seed}.json", control),
            (f"001-{seed}.json", candidate),
        ):
            path = folder / name
            path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(json.dumps({"receipt": str(path), "seed": seed, "policy": record["policy"],
                              "rank": record["placements"][0], "decisions": record["decisions"],
                              "freeze_actions": record["freeze_actions"]}), flush=True)
        control_records.append(control)
        candidate_records.append(candidate)
    delta = [c["placements"][0] - b["placements"][0]
             for c, b in zip(candidate_records, control_records)]
    metrics = {
        "session_id": SESSION_ID,
        "hypothesis": "one Freeze (action 2) before EndTurn on turns 4..9, when Refresh and Buy are illegal",
        "base_sha": "315b068bac5ab6d8403c3c9b18f8c101c0cded5d",
        "experiment_sha": os.environ.get("GITHUB_SHA", ""),
        "workflow_url": f"https://github.com/sstxww/reinforcement-learning/actions/runs/{os.getenv('GITHUB_RUN_ID', '')}",
        "engine": engine,
        "seeds": list(SEEDS),
        "training_steps": 0,
        "kind": "pure strategy ablation, no PPO training",
        "candidate": describe(candidate_records),
        "baseline": describe(control_records),
        "paired_delta_candidate_minus_baseline": delta,
        "mean_paired_delta": statistics.mean(delta),
        "paired_delta_stdev": statistics.stdev(delta) if len(delta) > 1 else None,
        "conclusion": "descriptive only; not evidence of statistical significance",
        "receipt_paths": [f"experiments/{SESSION_ID}/001-{s}.json" for s in SEEDS],
        "checkpoint": None,
    }
    metrics_path = Path("research/sessions") / SESSION_ID / "metrics-001.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
