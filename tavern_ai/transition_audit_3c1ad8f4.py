"""V5 read-only PUBLIC observation state-delta probe for model rank-eight diagnosis.

Same-turn observe2 fingerprints are *not* complete game-state equality, and legal BUY
exposures are not independent purchase opportunities or proof of optimal purchase.
Models are never changed/promoted; guarded completions are explicitly distinguished.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION = "s-20261102-3c1ad8f4"
ACTION_NAMES = {0: "end", 1: "refresh", 2: "freeze", 3: "upgrade"}
MAX_ACTIONS_PER_TURN = 85
HARD_ACTIONS_PER_TURN = 120


def family(action: int) -> str:
    if action in ACTION_NAMES:
        return ACTION_NAMES[action]
    if 8 <= action <= 15:
        return "buy"
    if 16 <= action <= 22:
        return "sell"
    if 46 <= action <= 125:
        return "play"
    if 196 <= action <= 244:
        return "move"
    return "other"


class TransitionCounts:
    """Counts mask-valid decisions, public state changes, and safety interventions."""

    def __init__(self):
        self.decisions = 0
        self.by_kind = defaultdict(Counter)
        self.by_turn = defaultdict(Counter)
        self.examples = []
        self.guard_ends = 0

    def record(self, *, turn: int, mask, action: int, before_f, before_c,
               after_f=None, after_c=None, same_turn: bool = False,
               forced: bool = False):
        mask = np.asarray(mask, dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise ValueError("Malformed or empty action mask")
        if type(action) is not int or not 0 <= action < ACTIONS or not mask[action]:
            raise ValueError("Illegal action")
        if type(turn) is not int or turn < 0:
            raise ValueError("Invalid turn")
        if forced and action != 0:
            raise ValueError("Guard can only force a legal END_TURN")
        buy_legal = bool(mask[8:16].any())
        kind = family(action)
        counts = self.by_kind[kind]
        t = self.by_turn[turn]
        self.decisions += 1
        counts["decisions"] += 1
        t["decisions"] += 1
        t["buy_legal_exposures"] += int(buy_legal)
        if kind == "buy":
            t["buys"] += 1
        if action == 0 and buy_legal:
            counts["end_with_legal_buy"] += 1
        if forced:
            self.guard_ends += 1
            counts["guard_forced"] += 1
        if not same_turn:
            counts["not_comparable_after_action"] += 1
            return
        if after_f is None or after_c is None:
            raise ValueError("Missing same-turn public observation")
        bf, af = np.asarray(before_f), np.asarray(after_f)
        bc, ac = np.asarray(before_c), np.asarray(after_c)
        if bf.shape != (FEATURES,) or af.shape != (FEATURES,):
            raise ValueError("Float observation contract mismatch")
        if bc.shape != (CARDS,) or ac.shape != (CARDS,):
            raise ValueError("Card observation contract mismatch")
        if not np.isfinite(bf).all() or not np.isfinite(af).all():
            raise ValueError("Non-finite public features")
        features_changed = int(np.count_nonzero(bf != af))
        cards_changed = int(np.count_nonzero(bc != ac))
        counts["same_turn_comparisons"] += 1
        counts["features_changed_total"] += features_changed
        counts["cards_changed_total"] += cards_changed
        key = "public_observation_changed" if features_changed or cards_changed else "public_observation_unchanged"
        counts[key] += 1
        if kind in {"refresh", "freeze", "move"} and len(self.examples) < 32:
            self.examples.append({
                "turn": turn, "action_id": action, "kind": kind,
                "features_changed": features_changed,
                "cards_changed": cards_changed, "buy_legal": buy_legal,
            })

    def summary(self) -> dict:
        return {
            "decisions": self.decisions,
            "guard_forced_ends": self.guard_ends,
            "action_families": {k: dict(sorted(v.items())) for k, v in sorted(self.by_kind.items())},
            "turns": {str(k): dict(sorted(v.items())) for k, v in sorted(self.by_turn.items())},
            "examples": self.examples,
            "limitations": [
                "A same-turn identical observe2 projection DOES NOT prove that internal game state was unchanged.",
                "BUY mask-legal exposures can repeat within a turn and are not independent offers or proof of a good purchase.",
                "Model games with any forced END_TURN are guarded, not raw policy results.",
            ],
        }


def run_game(seed: int, policy: str, model_path: Path | None,
             expected_sha256: str | None) -> tuple[dict, dict]:
    import taverngym
    engine = verify_engine()
    if policy not in {"baseline", "model"}:
        raise ValueError("Unsupported policy")
    model = None
    digest = None
    if policy == "model":
        if model_path is None or not model_path.is_file():
            raise FileNotFoundError("Model checkpoint required")
        if not expected_sha256 or len(expected_sha256) != 64:
            raise ValueError("An explicit expected model SHA256 is required")
        digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
        if digest != expected_sha256:
            raise ValueError("Model checkpoint digest mismatch")
        import torch
        from sb3_contrib import MaskablePPO
        torch.set_num_threads(2)
        model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    baseline = BaselinePolicy()
    trace = TransitionCounts()
    prior_turn = -1
    turn_actions = 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if prior_turn != turn:
            prior_turn, turn_actions = turn, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            floats, cards = game.observe2(0)
            before_f = np.frombuffer(floats, dtype="<f4").copy()
            before_c = np.frombuffer(cards, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if before_f.shape != (FEATURES,) or before_c.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned observe2/action-mask contract mismatch")
            if turn_actions >= HARD_ACTIONS_PER_TURN:
                raise RuntimeError("Unbounded policy loop reached the hard per-turn limit")
            forced = bool(policy == "model" and turn_actions >= MAX_ACTIONS_PER_TURN and mask[0])
            if forced:
                action = 0
            elif model is None:
                action = int(baseline.act(
                    {"features": before_f, "cards": before_c, "action_mask": mask},
                    {"turn": turn, "actions_used": turn_actions},
                ))
            else:
                selected, _ = model.predict(
                    {"features": before_f, "cards": before_c},
                    action_masks=mask, deterministic=True)
                action = int(np.asarray(selected).item())
            if not 0 <= action < ACTIONS or not mask[action]:
                raise ValueError("Policy produced illegal action")
            game.step(0, action)
            comparable = (not game.is_over() and int(game.turn) == turn and game.needs_action(0))
            after_f = after_c = None
            if comparable:
                next_floats, next_cards = game.observe2(0)
                after_f = np.frombuffer(next_floats, dtype="<f4").copy()
                after_c = np.frombuffer(next_cards, dtype="<i4").copy()
            trace.record(turn=turn, mask=mask, action=action, before_f=before_f, before_c=before_c,
                         after_f=after_f, after_c=after_c, same_turn=comparable, forced=forced)
            turn_actions += 1
        if not progressed and not game.is_over():
            raise RuntimeError("Simulator stalled")
    if not game.is_over():
        raise RuntimeError("Full eight-seat match failed to complete")
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION, "policy": "baseline" if model is None else "model_guarded" if trace.guard_ends else "model",
        "seed": seed, "completed": True, "turns": int(game.turn),
        "decisions": trace.decisions, "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "model_sha256": digest, "guard_forced_ends": trace.guard_ends,
    }
    validate(receipt)
    if sorted(receipt["placements"]) != list(range(1, 9)):
        raise ValueError("Invalid placements permutation")
    report = {
        "schema": 1, "seed": seed, "policy": receipt["policy"],
        "release_source": "v2-learning-41413557445" if model else None,
        "model_sha256": digest, "model_rank": receipt["placements"][0],
        "engine": engine, "telemetry": trace.summary(),
        "training_steps_this_run": 0,
        "competitive_gain_claim": False,
    }
    return receipt, report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--policy", choices=("baseline", "model"), required=True)
    p.add_argument("--model", type=Path)
    p.add_argument("--expected-sha256")
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    receipt, report = run_game(args.seed, args.policy, args.model, args.expected_sha256)
    for path, record in ((args.receipt, receipt), (args.report, report)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "seed": args.seed, "policy": receipt["policy"], "rank": receipt["placements"][0],
        "decisions": receipt["decisions"],
        "guard_forced_ends": receipt["guard_forced_ends"],
        "action_families": {k: v.get("decisions", 0) for k, v in report["telemetry"]["action_families"].items()},
    }))


if __name__ == "__main__":
    main()
