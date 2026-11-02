"""Real public-observation PPO behavior probe (never infer illegal opportunity from action count)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

FAMILIES = (
    ("end_turn", 0, 1), ("refresh", 1, 2), ("freeze", 2, 3),
    ("upgrade", 3, 4), ("hero_power", 4, 6),
    ("dark_gift", 6, 7), ("cancel", 7, 8),
    ("buy", 8, 16), ("sell", 16, 23), ("activate", 23, 30),
    ("choose", 30, 46), ("play", 46, 126),
    ("magnetize", 126, 196), ("move", 196, 245),
)


def family(action: int) -> str:
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError("Invalid action identifier")
    return next(name for name, lo, hi in FAMILIES if lo <= action < hi)


class OpportunityTrace:
    def __init__(self):
        self.per_turn = {}
        self.actions = Counter()
        self.total_decisions = 0
        self.buy_legal_decisions = 0
        self.end_with_legal_buy = 0
        self.max_consecutive_same = 0
        self._prev = None
        self._streak = 0

    def record(self, turn: int, mask, action: int):
        legal = np.asarray(mask, dtype=bool)
        if legal.shape != (ACTIONS,) or not legal.any() or not 0 <= action < ACTIONS or not legal[action]:
            raise ValueError("Illegal action or malformed legality mask")
        if type(turn) is not int or turn < 0:
            raise ValueError("Invalid game turn")
        current = self.per_turn.setdefault(turn, {
            "turn": turn, "decisions": 0, "buy_legal_decisions": 0,
            "buys": 0, "end_turns": 0, "end_with_legal_buy": 0,
            "actions_by_family": {},
        })
        kind = family(action)
        self.total_decisions += 1
        self.actions[kind] += 1
        current["decisions"] += 1
        current["actions_by_family"][kind] = current["actions_by_family"].get(kind, 0) + 1
        can_buy = bool(legal[8:16].any())
        self.buy_legal_decisions += int(can_buy)
        current["buy_legal_decisions"] += int(can_buy)
        if kind == "buy":
            current["buys"] += 1
        if kind == "end_turn":
            current["end_turns"] += 1
            if can_buy:
                self.end_with_legal_buy += 1
                current["end_with_legal_buy"] += 1
        if self._prev == (turn, action):
            self._streak += 1
        else:
            self._prev, self._streak = (turn, action), 1
        self.max_consecutive_same = max(self.max_consecutive_same, self._streak)

    def report(self) -> dict:
        turns = [self.per_turn[k] for k in sorted(self.per_turn)]
        return {
            "schema": 1,
            "decisions": self.total_decisions,
            "action_families": dict(sorted(self.actions.items())),
            "buy_legal_decisions": self.buy_legal_decisions,
            "buy_opportunity_turns": sum(t["buy_legal_decisions"] > 0 for t in turns),
            "actual_buys": self.actions["buy"],
            "model_end_turns": self.actions["end_turn"],
            "end_with_legal_buy": self.end_with_legal_buy,
            "max_consecutive_same_action_in_turn": self.max_consecutive_same,
            "by_turn": turns,
            "interpretation": (
                "A BUY was legal at these decision points; this does not prove that buying "
                "was strategically optimal. Repeated available BUY across one turn is not "
                "multiple independent purchase opportunities. No hidden-state input."
            ),
        }


def run_model_probe(model_path: Path, seed: int, agent_id: str):
    import taverngym
    from sb3_contrib import MaskablePPO
    engine = verify_engine()
    if not model_path.is_file() or not agent_id or "/" in agent_id:
        raise ValueError("Model path and safe agent ID required")
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    trace = OpportunityTrace()
    # Keep diagnostics finite even if an otherwise mask-legal model loops.
    decision_limit = 6000
    for _ in range(decision_limit):
        if game.is_over():
            break
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            floats, cards = game.observe2(0)
            features = np.frombuffer(floats, dtype="<f4").copy()
            card_ids = np.frombuffer(cards, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or card_ids.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned observation mismatch")
            action, _ = model.predict(
                {"features": features, "cards": card_ids},
                action_masks=mask, deterministic=True,
            )
            action = int(action)
            trace.record(int(game.turn), mask, action)
            game.step(0, action)
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        metrics = trace.report()
        metrics.update({
            "environment": "TavernGym", "seed": seed,
            "source_model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
            "complete_eight_seat_game": False, "model_controlled": True,
            "safety_fallback_count": 0,
            "diagnostic_iteration_limit": decision_limit,
            "last_observed_turn": int(game.turn),
            "failure_reason": "model_failed_to_finish_before_bounded_iteration_limit",
            "final_controlled_placement": None,
            "note": "Real policy observations; NOT a completed game or a valid match receipt.",
        })
        return None, metrics
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"], "agent_id": agent_id,
        "policy": "model", "seed": seed, "completed": True,
        "turns": int(game.turn), "decisions": trace.total_decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
    }
    validate(receipt)
    metrics = trace.report()
    metrics.update({
        "environment": "TavernGym", "seed": seed,
        "source_model_sha256": receipt["model_sha256"],
        "final_controlled_placement": receipt["placements"][0],
        "complete_eight_seat_game": True,
        "safety_fallback_count": 0,
        "model_controlled": True,
    })
    return receipt, metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    args = parser.parse_args()
    receipt, metrics = run_model_probe(args.model, args.seed, args.agent_id)
    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    args.metrics.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if receipt is None:
        print(json.dumps({
            "completed": False, "seed": args.seed,
            "failure_reason": metrics["failure_reason"],
            "decisions": metrics["decisions"],
            "buy_legal_decisions": metrics["buy_legal_decisions"],
            "actual_buys": metrics["actual_buys"],
            "end_with_legal_buy": metrics["end_with_legal_buy"],
        }), file=__import__("sys").stderr)
        raise SystemExit(3)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "completed": True, "placement": receipt["placements"][0],
        "decisions": metrics["decisions"], "buys": metrics["actual_buys"],
        "buy_legal_decisions": metrics["buy_legal_decisions"],
        "end_with_legal_buy": metrics["end_with_legal_buy"],
    }))


if __name__ == "__main__":
    main()
