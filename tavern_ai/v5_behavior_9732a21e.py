"""Pinned real-engine behavioral diagnosis; NO forced rescue and NO strength claim.

Failed/uncompleted candidate games are written as diagnostic records only, not
authentic game receipts. Policy sees observe2 and the legal action mask only.
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

ACTION_RANGES = (
    ("end_turn", 0, 1), ("refresh", 1, 2), ("freeze", 2, 3),
    ("upgrade", 3, 4), ("hero_power", 4, 6), ("dark_gift", 6, 7),
    ("cancel", 7, 8), ("buy", 8, 16), ("sell", 16, 23),
    ("activate", 23, 30), ("choose", 30, 46),
    ("play", 46, 126), ("magnetize", 126, 196), ("move", 196, 245),
)


def action_family(action: int) -> str:
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError("Unknown action index")
    return next(name for name, lo, hi in ACTION_RANGES if lo <= action < hi)


class TraceCounts:
    def __init__(self):
        self.categories = Counter()
        self.legal_families = Counter()
        self.turn_categories = {}
        self.legal_buy_decisions = 0
        self.legal_buy_end_turns = 0
        self.legal_buy_nonbuy_choices = 0
        self.gold_positive_legal_buy_ends = 0
        self.end_turn_gold = []
        self.same_public_observation = 0
        self.max_same_action_streak = 0
        self.max_same_public_observation_streak = 0
        self._last_action = None
        self._last_turn = None
        self._action_streak = 0
        self._last_digest = None
        self._public_streak = 0
        self.first_actions = []

    def record(self, turn: int, action: int, mask: np.ndarray, gold: float, digest: str):
        if mask.shape != (ACTIONS,) or mask.dtype != bool or not mask[action]:
            raise ValueError("Illegal action / action-mask mismatch")
        cat = action_family(action)
        self.categories[cat] += 1
        turn_key = str(turn)
        self.turn_categories.setdefault(turn_key, Counter())[cat] += 1
        for family, lo, hi in ACTION_RANGES:
            if bool(mask[lo:hi].any()):
                self.legal_families[family] += 1
        buy_legal = bool(mask[8:16].any())
        if buy_legal:
            self.legal_buy_decisions += 1
            if action == 0:
                self.legal_buy_end_turns += 1
                if gold > 0:
                    self.gold_positive_legal_buy_ends += 1
            if cat != "buy":
                self.legal_buy_nonbuy_choices += 1
        if action == 0:
            self.end_turn_gold.append(float(gold))
        if turn != self._last_turn:
            self._action_streak = 0
            self._last_action = None
            self._public_streak = 0
            self._last_digest = None
        if action == self._last_action:
            self._action_streak += 1
        else:
            self._action_streak = 1
        if digest == self._last_digest:
            self.same_public_observation += 1
            self._public_streak += 1
        else:
            self._public_streak = 1
        self.max_same_action_streak = max(self.max_same_action_streak, self._action_streak)
        self.max_same_public_observation_streak = max(
            self.max_same_public_observation_streak, self._public_streak
        )
        self._last_action = action
        self._last_turn = turn
        self._last_digest = digest
        if len(self.first_actions) < 32:
            self.first_actions.append({"turn": turn, "action": action,
                                       "family": cat, "buy_legal": buy_legal,
                                       "gold": float(gold)})

    def to_json(self):
        return {
            "chosen_action_families": dict(sorted(self.categories.items())),
            "legal_action_family_decisions": dict(sorted(self.legal_families.items())),
            "legal_buy_decisions": self.legal_buy_decisions,
            "legal_buy_end_turns": self.legal_buy_end_turns,
            "legal_buy_nonbuy_choices": self.legal_buy_nonbuy_choices,
            "gold_positive_legal_buy_ends": self.gold_positive_legal_buy_ends,
            "end_turn_gold_mean": (statistics.mean(self.end_turn_gold)
                                   if self.end_turn_gold else None),
            "same_public_observation_transitions": self.same_public_observation,
            "max_same_public_observation_streak": self.max_same_public_observation_streak,
            "max_same_action_streak": self.max_same_action_streak,
            "turn_action_families": {k: dict(v) for k, v in self.turn_categories.items()},
            "first_actions": self.first_actions,
        }


def run_trace(seed: int, policy: str, model, model_sha: str | None, agent_id: str):
    import taverngym

    if policy not in ("model", "baseline"):
        raise ValueError("Invalid policy name")
    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    baseline = BaselinePolicy()
    stats = TraceCounts()
    actions_this_turn = 0
    last_turn = -1
    decisions = 0
    failure = None
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if last_turn != turn:
            last_turn, actions_this_turn = turn, 0
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
                raise ValueError("Engine contract mismatch")
            if not np.isfinite(features).all():
                raise ValueError("Non-finite public observation")
            if policy == "model":
                proposed, _ = model.predict({"features": features, "cards": cards},
                                            action_masks=mask, deterministic=True)
                action = int(np.asarray(proposed).item())
            else:
                action = int(baseline.act({"features": features, "cards": cards,
                                           "action_mask": mask},
                                          {"turn": turn, "actions_used": actions_this_turn}))
            digest = hashlib.sha256(fb + cb + mask.astype(np.uint8).tobytes()).hexdigest()
            # features[7]: own public gold at the pinned TavernGym 1.1.0 contract.
            stats.record(turn, action, mask, float(features[7]), digest)
            game.step(0, action)
            actions_this_turn += 1
            decisions += 1
        if not progressed and not game.is_over():
            failure = "game_stalled"
            break
    if not game.is_over() and failure is None:
        failure = "full_game_safety_limit_exceeded"
    if game.is_over() and (int(game.truncated_combats) or bool(game.turn_limit_end)):
        failure = "simulator_guard_triggered"
    diagnostic = {
        "seed": seed, "policy": policy, "source": "real_pinned_taverngym_game",
        "model_sha256": model_sha, "completed": bool(game.is_over()) and failure is None,
        "failure": failure, "turns_reached": int(game.turn),
        "decisions": decisions, "trace": stats.to_json(),
        "engine": engine, "no_fallback": policy == "model",
    }
    if diagnostic["completed"]:
        receipt = {
            "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": "TavernGym", "engine_source_hash": engine["source_hash"],
            "engine_version": engine["version"], "agent_id": agent_id, "policy": policy,
            "seed": seed, "completed": True, "turns": int(game.turn),
            "decisions": decisions,
            "placements": [int(v) for v in game.placements()],
            "truncated_combats": 0, "turn_limit_end": False,
            "git_sha": os.getenv("GITHUB_SHA", ""),
            "model_sha256": model_sha,
        }
        validate_integrity(receipt)
        diagnostic["rank"] = receipt["placements"][0]
        return diagnostic, receipt
    # Never return fabricated placements or a receipt on an incomplete game.
    return diagnostic, None


def study(model_path: Path, seed_start: int, games: int, agent_id: str,
          receipt_dir: Path, report_path: Path):
    from sb3_contrib import MaskablePPO
    if not 1 <= games <= 3:
        raise ValueError("This diagnostic is bounded to 1..3 paired seeds")
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    model = MaskablePPO.load(str(model_path), device="cpu")
    receipt_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for seed in range(seed_start, seed_start + games):
        for policy in ("model", "baseline"):
            diagnostic, receipt = run_trace(seed, policy,
                                            model if policy == "model" else None,
                                            model_hash if policy == "model" else None,
                                            agent_id)
            entries.append(diagnostic)
            if receipt is not None:
                path = receipt_dir / f"002-{seed}-{policy}.json"
                path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"seed": seed, "policy": policy,
                               "completed": diagnostic["completed"],
                               "failure": diagnostic["failure"],
                               "rank": diagnostic.get("rank"),
                               "trace": diagnostic["trace"]}, ensure_ascii=False), flush=True)
    pairs = []
    for seed in range(seed_start, seed_start + games):
        m = next(v for v in entries if v["seed"] == seed and v["policy"] == "model")
        b = next(v for v in entries if v["seed"] == seed and v["policy"] == "baseline")
        if m["completed"] and b["completed"]:
            pairs.append({"seed": seed, "candidate_rank": m["rank"],
                          "baseline_rank": b["rank"], "delta": m["rank"] - b["rank"]})
    report = {
        "schema": 1, "session_id": agent_id, "source_run": 41427627265,
        "experiment": "pure_model_public_buy_opportunity_and_loop_diagnostic",
        "model_sha256": model_hash, "heldout_seeds": list(range(seed_start, seed_start + games)),
        "candidate_games_completed": sum(v["completed"] for v in entries if v["policy"] == "model"),
        "candidate_games_failed": sum(not v["completed"] for v in entries if v["policy"] == "model"),
        "paired_completed_count": len(pairs),
        "paired_results": pairs,
        "paired_mean_delta": (statistics.mean(v["delta"] for v in pairs) if pairs else None),
        "entries": entries,
        "failure_is_not_rank": True,
        "model_promotion": False,
        "interpretation": "Exploratory diagnostic; no fallback; incomplete games have no rank.",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"candidate_completed": report["candidate_games_completed"],
                      "candidate_failed": report["candidate_games_failed"],
                      "paired_completed": report["paired_completed_count"]}), flush=True)
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--seed-start", type=int, default=83701)
    p.add_argument("--games", type=int, default=2)
    p.add_argument("--agent-id", default="s-20261102-9732a21e")
    p.add_argument("--receipt-dir", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    study(a.model, a.seed_start, a.games, a.agent_id, a.receipt_dir, a.report)


if __name__ == "__main__":
    main()
