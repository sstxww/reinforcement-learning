"""Bounded raw-PPO public-state Play/Cancel cycle audit; not an intervention."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def digest(public_bytes: bytes) -> str:
    if not isinstance(public_bytes, bytes):
        raise TypeError("Expected public observation bytes")
    return hashlib.sha256(public_bytes).hexdigest()


class CycleTrace:
    """Count Play/Cancel pairs separately from exact public state-return pairs.

    State return covers controlled-seat observe2 and legal mask bytes; it does not
    establish that hidden state is identical. Never join evidence across turns.
    """
    def __init__(self):
        self.turn = None
        self.previous = None
        self.last_return_start = None
        self.counts = Counter()
        self.per_turn = {}
        self.examples = []

    def record(self, turn: int, action: int, legal, before: bytes,
               after: bytes | None) -> None:
        mask = tuple(bool(x) for x in legal)
        if type(turn) is not int or turn < 0 or type(action) is not int:
            raise ValueError("Invalid turn or action type")
        if len(mask) != 245 or action not in range(245) or not mask[action]:
            raise ValueError("Illegal raw action or malformed pinned mask")
        if after is not None and not isinstance(after, bytes):
            raise TypeError("Expected public observation bytes after step")
        if turn != self.turn:
            self.turn, self.previous, self.last_return_start = turn, None, None
        family = "play" if 46 <= action < 126 else "cancel" if action == 7 else "other"
        before_hash = digest(before)
        after_hash = digest(after) if after is not None else None
        self.counts["raw_decisions"] += 1
        self.counts["legal_buy_decisions"] += int(any(mask[8:16]))
        self.counts["chosen_buy_decisions"] += int(8 <= action < 16)
        self.counts["raw_play_actions"] += int(family == "play")
        self.counts["raw_cancel_actions"] += int(family == "cancel")
        turn_counts = self.per_turn.setdefault(str(turn), Counter())
        turn_counts["decisions"] += 1
        if family == "cancel" and self.previous is not None and self.previous[0] == "play":
            self.counts["adjacent_play_cancel_pairs"] += 1
            turn_counts["adjacent_play_cancel_pairs"] += 1
            _, prev_before, prev_after = self.previous
            continuous = prev_after is not None and prev_after == before_hash
            returned = continuous and after_hash is not None and prev_before == after_hash
            if returned:
                self.counts["exact_public_state_return_pairs"] += 1
                turn_counts["exact_public_state_return_pairs"] += 1
                if self.last_return_start == prev_before:
                    self.counts["repeated_exact_state_return_pairs"] += 1
                    turn_counts["repeated_exact_state_return_pairs"] += 1
                self.last_return_start = prev_before
                if len(self.examples) < 12:
                    self.examples.append({"turn": turn, "start_public_sha256": prev_before,
                                          "after_play_public_sha256": before_hash,
                                          "after_cancel_public_sha256": after_hash})
            else:
                self.last_return_start = None
        elif family == "other":
            self.last_return_start = None
        self.previous = (family, before_hash, after_hash)

    def report(self) -> dict:
        keys = ("raw_decisions", "legal_buy_decisions", "chosen_buy_decisions",
                "raw_play_actions", "raw_cancel_actions", "adjacent_play_cancel_pairs",
                "exact_public_state_return_pairs", "repeated_exact_state_return_pairs")
        return {"schema": 1, "policy_provenance": "raw_model_unassisted",
                "counters": {k: self.counts[k] for k in keys},
                "per_turn": {t: dict(v) for t, v in self.per_turn.items()},
                "examples": self.examples,
                "interpretation": "Exact return compares controlled-seat observe2 plus legal mask; it does not prove identical hidden state, strategic strength, or causal root. BUY-legal decisions are correlated, not independent opportunities."}


def run_probe(model_file: Path, seed: int, max_model_decisions: int) -> dict:
    import numpy as np
    import taverngym
    from sb3_contrib import MaskablePPO
    from .contract import ACTIONS, CARDS, FEATURES, verify_engine

    if not 32 <= max_model_decisions <= 1200 or seed < 0:
        raise ValueError("Bounded max_model_decisions must be 32..1200")
    engine = verify_engine()
    model_sha256 = hashlib.sha256(model_file.read_bytes()).hexdigest()
    model = MaskablePPO.load(str(model_file), device="cpu")
    game = taverngym.Game(seed=seed)
    trace = CycleTrace()
    limit_hit = False
    for _ in range(30000):
        if game.is_over():
            break
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            turn = int(game.turn)
            f, c = game.observe2(0)
            mask_raw = game.legal_mask(0)
            floats = np.frombuffer(f, dtype="<f4").copy()
            cards = np.frombuffer(c, dtype="<i4").copy()
            mask = np.frombuffer(mask_raw, dtype=np.uint8).astype(bool)
            if floats.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned observation / legal mask contract changed")
            raw, _ = model.predict({"features": floats, "cards": cards},
                                   action_masks=mask, deterministic=True)
            action = int(np.asarray(raw).item())
            before = f + c + bytes(mask_raw)
            if not 0 <= action < ACTIONS or not mask[action]:
                raise ValueError("Raw model selected an illegal action")
            game.step(0, action)
            after = None
            if not game.is_over() and int(game.turn) == turn and game.needs_action(0):
                ff, cc = game.observe2(0)
                mm = game.legal_mask(0)
                after = ff + cc + bytes(mm)
            trace.record(turn, action, mask, before, after)
            if trace.counts["raw_decisions"] >= max_model_decisions and not game.is_over():
                limit_hit = True
                break
        if limit_hit:
            break
        if not progressed and not game.is_over():
            raise RuntimeError("Engine made no progress")
    complete = bool(game.is_over())
    output = trace.report()
    output.update({"environment": "TavernGym", "engine_version": engine["version"],
                   "engine_source_hash": engine["source_hash"],
                   "model_sha256": model_sha256, "seed": seed, "controlled_seat": 0,
                   "opponents": "seven native scripted bots", "raw_model_complete": complete,
                   "max_model_decisions": max_model_decisions, "fallback_actions": 0,
                   "guard_interventions": 0, "new_training_steps": 0,
                   "diagnostic_stop_reason": None if complete else (
                       "model_decision_budget_exhausted" if limit_hit else "engine_outer_iteration_limit"),
                   "placement": int(game.placements()[0]) if complete else None,
                   "placements": [int(x) for x in game.placements()] if complete else None,
                   "not_a_receipt": True,
                   "note": "Incomplete raw probes have no rank. Even if complete, this analytic summary is not a canonical validated receipt."})
    if complete and sorted(output["placements"]) != list(range(1, 9)):
        raise ValueError("Non-permutation completed game placements")
    return output


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--max-model-decisions", type=int, default=384)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    report = run_probe(a.model, a.seed, a.max_model_decisions)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"completed": report["raw_model_complete"],
                      "placement": report["placement"], "counters": report["counters"],
                      "model_sha256": report["model_sha256"],
                      "stop_reason": report["diagnostic_stop_reason"]}), flush=True)


if __name__ == "__main__":
    main()
