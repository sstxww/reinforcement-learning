"""Opportunity-aware real eight-seat diagnosis of a pinned, unpromoted PPO V2 Release.

All policy inputs are the own-seat observe2 arrays and legal-action mask.
Own-seat Game.view is used ONLY for post-hoc audit fields, never for inference.
Guarded results cannot be presented as raw policy performance or a promotion.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import statistics

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .receipt_integrity import validate_integrity

SESSION = "s-20261102-90e24c7b"
V2_TAG = "v2-learning-41413557445"
V2_SHA256 = "73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a"
SEEDS = (89101, 89102, 89103)
MAX_PER_TURN = 75

FAMILIES = (
    (0, 1, "end"), (1, 2, "refresh"), (2, 3, "freeze"),
    (3, 4, "upgrade"), (4, 6, "hero_power"), (6, 7, "dark_gift"),
    (7, 8, "cancel"), (8, 16, "buy"), (16, 23, "sell"),
    (23, 30, "activate"), (30, 46, "choose"),
    (46, 126, "play"), (126, 196, "magnetize"),
    (196, 245, "move"),
)


def action_family(action: int) -> str:
    if not isinstance(action, int) or not 0 <= action < ACTIONS:
        raise ValueError("action outside pinned legal vocabulary")
    return next(label for low, high, label in FAMILIES if low <= action < high)


def load_verified_model(path: Path):
    from sb3_contrib import MaskablePPO
    if not path.is_file():
        raise FileNotFoundError(path)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != V2_SHA256:
        raise ValueError(f"V2 Release model SHA256 mismatch: {sha}")
    model = MaskablePPO.load(str(path), device="cpu")
    if int(model.num_timesteps) != 1280:
        raise ValueError("Unexpected V2 checkpoint step count")
    return model


def own_snapshot(game) -> dict:
    """Read only public/own-seat debug view as diagnostic metadata."""
    own = json.loads(game.view(0))["me"]
    return {
        "gold": own.get("gold"),
        "tier": own.get("tier"),
        "board_size": len(own.get("board") or []),
        "hand_size": len(own.get("hand") or []),
    }


def play(seed: int, label: str, engine: dict, model=None) -> dict:
    import taverngym
    if label not in ("model", "baseline"):
        raise ValueError("Invalid arm")
    if label == "model" and model is None:
        raise ValueError("Missing model")
    game = taverngym.Game(seed=seed)
    baseline = BaselinePolicy()
    family_counts = Counter()
    allowed = Counter()
    selected_with_opportunity = Counter()
    legal_buy_turns = set()
    ended_with_buy_available = 0
    guard_forced_ends = 0
    decisions = 0
    last_turn = None
    used = 0
    per_turn = {}
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, used = turn, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(0)
            features = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Wrong policy observation/action contract")
            if not mask.any() or not np.isfinite(features).all():
                raise ValueError("Invalid policy observation or empty legal action mask")
            snap = own_snapshot(game)
            row = per_turn.setdefault(str(turn), {
                "first_own_view": snap,
                "decisions": 0, "legal_buy_decisions": 0, "buy_actions": 0,
                "end_with_buy_legal": 0, "guard_forced_ends": 0,
            })
            row["decisions"] += 1
            available = {name: any(mask[lo:hi]) for lo, hi, name in FAMILIES}
            for name, yes in available.items():
                if yes:
                    allowed[name] += 1
            if available["buy"]:
                legal_buy_turns.add(turn)
                row["legal_buy_decisions"] += 1
            forced = False
            if used >= MAX_PER_TURN and mask[0]:
                action = 0
                forced = True
            elif used >= 120:
                raise RuntimeError("Per-turn policy nontermination; no valid full game")
            elif label == "model":
                choice, _ = model.predict(
                    {"features": features, "cards": cards},
                    action_masks=mask, deterministic=True,
                )
                action = int(np.asarray(choice).item())
            else:
                action = int(baseline.act(
                    {"features": features, "cards": cards, "action_mask": mask},
                    {"turn": turn, "actions_used": used},
                ))
            if not (0 <= action < ACTIONS and mask[action]):
                raise ValueError("Policy selected illegal action")
            family = action_family(action)
            family_counts[family] += 1
            if available[family]:
                selected_with_opportunity[family] += 1
            if family == "buy":
                row["buy_actions"] += 1
            if action == 0 and available["buy"]:
                ended_with_buy_available += 1
                row["end_with_buy_legal"] += 1
            if forced:
                guard_forced_ends += 1
                row["guard_forced_ends"] += 1
            if action == 0:
                row["gold_before_end"] = snap["gold"]
                row["board_before_end"] = snap["board_size"]
            game.step(0, action)
            used += 1
            decisions += 1
        if not progressed and not game.is_over():
            raise RuntimeError("Eight-seat simulator stalled")
    if not game.is_over():
        raise RuntimeError("Full eight-seat match safety limit exceeded")
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION,
        "policy": label,
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(v) for v in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": V2_SHA256 if label == "model" else None,
        "model_tag": V2_TAG if label == "model" else None,
        "model_controlled_with_legal_end_guard": label == "model",
        "guard_forced_ends": guard_forced_ends,
        "action_family_counts": dict(sorted(family_counts.items())),
        "legal_family_decisions": dict(sorted(allowed.items())),
        "selected_with_family_legal": dict(sorted(selected_with_opportunity.items())),
        "legal_buy_decisions": allowed["buy"],
        "legal_buy_turn_count": len(legal_buy_turns),
        "buy_actions": family_counts["buy"],
        "end_with_buy_available": ended_with_buy_available,
        "per_turn_own_view": per_turn,
        "note": "Opportunity counts are per decision, NOT independent purchase opportunities. Own-view fields never enter policy.",
    }
    validate_integrity(receipt)
    return receipt


def aggregate(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("No completed games")
    for r in rows:
        validate_integrity(r)
    ranks = [r["placements"][0] for r in rows]
    legal = sum(r["legal_buy_decisions"] for r in rows)
    bought = sum(r["buy_actions"] for r in rows)
    return {
        "games": len(rows),
        "ranks": ranks,
        "mean_rank": statistics.mean(ranks),
        "top4_rate": sum(v <= 4 for v in ranks) / len(ranks),
        "first_rate": sum(v == 1 for v in ranks) / len(ranks),
        "decisions": sum(r["decisions"] for r in rows),
        "buy_legal_decisions": legal,
        "buy_legal_turns": sum(r["legal_buy_turn_count"] for r in rows),
        "selected_buy_actions": bought,
        "buy_per_legal_decision": bought / legal if legal else None,
        "ends_while_buy_legal": sum(r["end_with_buy_available"] for r in rows),
        "guard_forced_ends": sum(r["guard_forced_ends"] for r in rows),
    }


def write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    import torch
    torch.set_num_threads(2)
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("reports") / SESSION / "001-opportunities.json")
    parser.add_argument("--seed-start", type=int, default=SEEDS[0])
    args = parser.parse_args()
    engine = verify_engine()
    model = load_verified_model(args.model)
    seeds = tuple(args.seed_start + i for i in range(3))
    both = {}
    for arm in ("baseline", "model"):
        both[arm] = []
        for seed in seeds:
            result = play(seed, arm, engine, model if arm == "model" else None)
            target = Path("experiments") / SESSION / f"001-{arm}-{seed}.json"
            write(target, result)
            both[arm].append(result)
            print(f"{arm} seed={seed} rank={result['placements'][0]} buy={result['buy_actions']} "
                  f"legal-buy-decisions={result['legal_buy_decisions']} guard={result['guard_forced_ends']}", flush=True)
    report = {
        "session_id": SESSION, "schema": 1,
        "engine": engine,
        "release": V2_TAG, "model_sha256": V2_SHA256,
        "source_training_steps": 1280, "new_training_steps": 0,
        "seeds": seeds, "evaluation_type": "three independent heldout seed-paired real games",
        "baseline": aggregate(both["baseline"]),
        "model_guarded": aggregate(both["model"]),
        "paired_delta_rank_model_minus_baseline": [
            m["placements"][0] - b["placements"][0]
            for m, b in zip(both["model"], both["baseline"])
        ],
        "limitations": [
            "Offline own-view diagnostics; no hidden state enters the policy.",
            "Guard-triggered model outcomes must be reported separately from raw policy.",
            "Repeated legal-buy decisions are not independent buying opportunities.",
            "Three seeds are a diagnostic pilot, NOT evidence of model superiority.",
        ],
        "champion_promoted": False,
    }
    write(args.out, report)
    print(json.dumps({"baseline": report["baseline"], "model_guarded": report["model_guarded"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
