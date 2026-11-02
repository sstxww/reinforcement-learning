"""Round 002: real-engine three-arm public-shop-value Freeze ablation."""
from __future__ import annotations
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from tavern_ai.baseline import BaselinePolicy
from tavern_ai.contract import ACTIONS, FEATURES, CARDS, verify_engine
from tavern_ai.validate_receipt import validate

SESSION_ID = "s-20261102-717d0e50"
SEEDS = range(29201, 29211)
ARMS = ("baseline", "blind-freeze", "quality-freeze")
BASE = BaselinePolicy()


def verify_public_observation_layout(layout: dict) -> None:
    """Check both public observation versions; observe2 is not V1's prefix layout."""
    if (layout.get("OBS2_FLOATS"), layout.get("OBS2_CARDS"), layout.get("N_ACTIONS")) != (FEATURES, CARDS, ACTIONS):
        raise RuntimeError(f"Unexpected observe2 contract: {layout}")
    if (layout.get("OBS_FLOATS"), layout.get("OBS_CARDS"), layout.get("GLOBAL_F"),
            layout.get("ITEM_F"), layout.get("MINION_F"), layout.get("N_SHOP"),
            layout.get("N_HAND"), layout.get("N_BOARD")) != (3227, 124, 53, 40, 31, 8, 10, 7):
        raise RuntimeError(f"Unexpected legacy public shop layout: {layout}")


def shop_start(layout: dict) -> int:
    return (layout["GLOBAL_F"] + layout["N_QUESTS"] * layout["QUEST_F"]
            + layout["PENDING_KINDS"] + layout["N_BOARD"] * layout["MINION_F"]
            + layout["N_HAND"] * layout["ITEM_F"])


def shop_is_valuable(features: np.ndarray, layout: dict) -> bool:
    """Use public observe2 shop tier and attack/health, never hidden opponent state."""
    if features[15] > 0.5:  # already frozen: do not inadvertently unfreeze
        return False
    stride = layout["ITEM_F"]
    start = shop_start(layout)
    rows = features[start:start + layout["N_SHOP"] * stride].reshape(layout["N_SHOP"], stride)
    tier_now = round(float(features[10]) * 6)
    minimum_tier = max(2, tier_now - 1)
    present_minion = (rows[:, 0] > 0.5) & (rows[:, 1] > 0.5)
    tiers = rows[:, 13] * 6.0
    combined_stats = (rows[:, 10] + rows[:, 11]) * 10.0
    return bool(np.any(present_minion & (tiers >= minimum_tier - 0.01) & (combined_stats >= 4.99)))


def select_action(features: np.ndarray, mask: np.ndarray, turn: int, actions_used: int,
                  froze_this_turn: bool, arm: str, layout: dict) -> int:
    if arm not in ARMS:
        raise ValueError(f"Unknown arm {arm}")
    action = BASE.act({"action_mask": mask}, {"turn": turn, "actions_used": actions_used})
    can_freeze = (
        arm != "baseline" and action == 0 and 4 <= turn <= 9
        and not froze_this_turn and actions_used < 85
        and mask[2] and not mask[1] and not mask[8:16].any()
    )
    if can_freeze and (arm == "blind-freeze" or shop_is_valuable(features, layout)):
        return 2
    return action


def game_receipt(seed: int, arm: str, engine: dict, layout: dict) -> dict:
    import taverngym
    game = taverngym.Game(seed=seed)
    decisions = 0
    freeze_count = 0
    last_turn = -1
    actions_used = 0
    froze_this_turn = False
    for _ in range(30_000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, actions_used, froze_this_turn = turn, 0, False
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(0)
            features = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError(f"observe2 shape mismatch at seed {seed}")
            if not np.isfinite(features).all() or not mask.any():
                raise ValueError("Invalid features or empty action mask")
            # observe2 is 4017 floats, but its flattened feature layout is not
            # the 3227-float legacy layout. Read the *same seat's public* V1
            # observation only for correct shop feature offsets.
            public_bytes, _ = game.observe(0)
            public_features = np.frombuffer(public_bytes, dtype="<f4").copy()
            if public_features.shape != (layout["OBS_FLOATS"],) or not np.isfinite(public_features).all():
                raise ValueError(f"Invalid legacy public shop observation, seed={seed}")
            action = select_action(public_features, mask, turn, actions_used, froze_this_turn, arm, layout)
            if not mask[action]:
                raise ValueError(f"Illegal action {action}, {arm}, seed {seed}, turn {turn}")
            game.step(0, action)
            decisions += 1
            actions_used += 1
            if action == 2:
                freeze_count += 1
                froze_this_turn = True
        if not progress and not game.is_over():
            raise RuntimeError(f"Game stalled: seed={seed}, arm={arm}")
    if not game.is_over():
        raise RuntimeError(f"Full-game safety cap exceeded: seed={seed}, arm={arm}")
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION_ID, "policy": arm, "seed": seed,
        "completed": True, "turns": int(game.turn),
        "decisions": decisions, "placements": [int(p) for p in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end), "illegal_actions": 0,
        "freeze_actions": freeze_count, "action_cap": 85,
        "model_sha256": None, "git_sha": os.getenv("GITHUB_SHA", ""),
    }
    validate(receipt)
    return receipt


def summarize(records: list[dict]) -> dict:
    ranks = [r["placements"][0] for r in records]
    return {
        "games": len(records), "mean_rank": statistics.mean(ranks), "ranks": ranks,
        "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
        "first_place_rate": sum(x == 1 for x in ranks) / len(ranks),
        "decisions": sum(r["decisions"] for r in records),
        "freeze_actions": sum(r["freeze_actions"] for r in records),
    }


def main() -> None:
    import taverngym
    engine = verify_engine()
    layout = dict(taverngym.layout())
    # Fail closed if the public observation layout changes unexpectedly.
    verify_public_observation_layout(layout)
    if shop_start(layout) + layout["N_SHOP"] * layout["ITEM_F"] > FEATURES:
        raise RuntimeError("Shop offsets exceed observe2 bounds")
    path = Path("experiments") / SESSION_ID
    path.mkdir(parents=True, exist_ok=True)
    records = {a: [] for a in ARMS}
    for seed in SEEDS:
        for arm in ARMS:
            receipt = game_receipt(seed, arm, engine, layout)
            prefix = {"baseline": "control2", "blind-freeze": "blind2",
                      "quality-freeze": "002"}[arm]
            location = path / f"{prefix}-{seed}.json"
            location.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            records[arm].append(receipt)
            print(json.dumps({"receipt": str(location), "arm": arm, "seed": seed,
                  "rank": receipt["placements"][0], "freeze_actions": receipt["freeze_actions"],
                  "decisions": receipt["decisions"]}), flush=True)
    baseline = [p["placements"][0] for p in records["baseline"]]
    blind = [p["placements"][0] for p in records["blind-freeze"]]
    quality = [p["placements"][0] for p in records["quality-freeze"]]
    metrics = {
        "session_id": SESSION_ID, "round": 2,
        "base_sha": "315b068bac5ab6d8403c3c9b18f8c101c0cded5d",
        "source_sha": os.getenv("GITHUB_SHA", ""),
        "workflow_url": f"https://github.com/sstxww/reinforcement-learning/actions/runs/{os.getenv('GITHUB_RUN_ID', '')}",
        "engine": engine, "layout": layout, "seeds": list(SEEDS),
        "method": "public-observation shop quality gate, tier>=max(2, tavern tier-1), attack+health>=5, already-frozen safeguard",
        "training_steps": 0, "checkpoint": None,
        "arms": {a: summarize(records[a]) for a in ARMS},
        "quality_minus_baseline": [a - b for a, b in zip(quality, baseline)],
        "quality_minus_blind": [a - b for a, b in zip(quality, blind)],
        "conclusion": "descriptive only; no strength claim without larger independent holdout",
    }
    destination = Path("research/sessions") / SESSION_ID / "metrics-002.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2), flush=True)


if __name__ == "__main__":
    main()
