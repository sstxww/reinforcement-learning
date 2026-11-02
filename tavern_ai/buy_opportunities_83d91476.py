"""Real-game legal-action opportunity telemetry; no policy modifications.

Counters are *decision exposures*, not independent shopping opportunities or
economic value estimates. The buy action band is the pinned contract's 8..15.
For other semantics, preserve raw IDs instead of guessing intent.
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

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION = "s-20261102-83d91476"
BUY_ACTIONS = range(8, 16)
TURN_BUDGET = 85
HARD_TURN_LIMIT = 120


class Opportunities:
    """Track opportunities before each action, including forced-end provenance."""

    def __init__(self):
        self.stats = Counter()
        self.action_ids = Counter()
        self.turns = {}
        self.first_actions = []

    def observe(self, turn: int, mask, action: int, *, forced: bool = False):
        if len(mask) != ACTIONS or not any(mask):
            raise ValueError("Invalid or empty 245-action mask")
        if type(action) is not int or not (0 <= action < ACTIONS) or not bool(mask[action]):
            raise ValueError("Illegal action; cannot interpret telemetry")
        if forced and action != 0:
            raise ValueError("Guard override must be a legal END_TURN")
        buy_legal = any(bool(mask[i]) for i in BUY_ACTIONS)
        chosen_buy = action in BUY_ACTIONS
        row = self.turns.setdefault(str(turn), dict(decisions=0, buy_legal_exposures=0,
            buys=0, ends_with_buy_legal=0, forced_ends=0))
        row["decisions"] += 1
        self.stats["decisions"] += 1
        if buy_legal:
            row["buy_legal_exposures"] += 1
            self.stats["buy_legal_exposures"] += 1
        if chosen_buy:
            row["buys"] += 1
            self.stats["buys"] += 1
        if action == 0:
            self.stats["end_turn"] += 1
            if forced:
                row["forced_ends"] += 1
                self.stats["guard_forced_end"] += 1
            else:
                self.stats["policy_chosen_end"] += 1
                if buy_legal:
                    row["ends_with_buy_legal"] += 1
                    self.stats["policy_end_with_buy_legal"] += 1
        if action == 3:
            self.stats["tavern_upgrade"] += 1
        if 46 <= action < 126:
            self.stats["hand_play_band"] += 1
        self.action_ids[str(action)] += 1
        if len(self.first_actions) < 30:
            self.first_actions.append(action)

    def report(self) -> dict:
        s = self.stats
        return {
            "counts": dict(sorted(s.items())),
            "buy_legal_turns": sum(v["buy_legal_exposures"] > 0 for v in self.turns.values()),
            "turns_with_buy": sum(v["buys"] > 0 for v in self.turns.values()),
            "buy_given_legal_exposure_rate": (
                s["buys"] / s["buy_legal_exposures"] if s["buy_legal_exposures"] else None
            ),
            "per_turn": self.turns,
            "action_histogram": dict(sorted(self.action_ids.items(), key=lambda x: int(x[0]))),
            "first_actions": self.first_actions,
            "denominator_note": (
                "Each seat-0 decision with >=1 legal buy action counts as one exposure. "
                "Exposures are correlated and do not imply affordability or card quality. "
                "End-with-buy means an END_TURN was selected while BUY was mask-legal."
            ),
        }


def real_game(seed: int, policy: str, model=None, model_hash: str | None = None) -> dict:
    import numpy as np
    import taverngym
    from .baseline import BaselinePolicy

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    baseline = BaselinePolicy()
    telemetry = Opportunities()
    last_turn, turn_actions = -1, 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, turn_actions = turn, 0
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
                raise ValueError("Observation contract mismatch")
            if not np.isfinite(features).all():
                raise ValueError("Nonfinite observation")
            if turn_actions >= HARD_TURN_LIMIT:
                raise RuntimeError(f"Turn loop limit seed={seed} turn={turn}")
            forced = bool(policy == "model" and turn_actions >= TURN_BUDGET and mask[0])
            if forced:
                action = 0
            elif policy == "baseline":
                action = int(baseline.act(
                    {"features": features, "cards": cards, "action_mask": mask},
                    {"turn": turn, "actions_used": turn_actions},
                ))
            elif policy == "model" and model is not None:
                selected, _ = model.predict(
                    {"features": features, "cards": cards},
                    action_masks=mask, deterministic=True,
                )
                action = int(np.asarray(selected).item())
            else:
                raise ValueError("Model required for model policy")
            telemetry.observe(turn, mask, action, forced=forced)
            game.step(0, action)
            turn_actions += 1
        if not progressed and not game.is_over():
            raise RuntimeError(f"Game stalled seed={seed}")
    if not game.is_over():
        raise RuntimeError(f"Full-game safety limit seed={seed}")
    diagnostics = telemetry.report()
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION,
        "policy": "model_guarded" if policy == "model" else "baseline",
        "seed": seed, "completed": True, "turns": int(game.turn),
        "decisions": diagnostics["counts"].get("decisions", 0),
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": model_hash,
        "guarded": diagnostics["counts"].get("guard_forced_end", 0) > 0,
        "opportunity_diagnostics": diagnostics,
    }
    validate(result)
    if sorted(result["placements"]) != list(range(1, 9)):
        raise ValueError("Invalid placement permutation")
    return result


def summary(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("No completed games")
    for row in rows:
        validate(row)
    ranks = [r["placements"][0] for r in rows]
    totals = Counter()
    for r in rows:
        totals.update(r["opportunity_diagnostics"]["counts"])
    return {
        "games": len(rows), "ranks": ranks,
        "mean_rank": statistics.mean(ranks),
        "top4_rate": sum(n <= 4 for n in ranks) / len(ranks),
        "total_buy_legal_exposures": totals["buy_legal_exposures"],
        "total_buys": totals["buys"],
        "policy_ends_with_legal_buy": totals["policy_end_with_buy_legal"],
        "guard_forced_ends": totals["guard_forced_end"],
        "candidate_pure_model_games": sum(not r["guarded"] for r in rows),
        "note": "Descriptive matched seeds only; small n cannot establish strength or cause.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--seeds", nargs="+", type=int, default=[45111, 45112])
    p.add_argument("--out", type=Path, default=Path("outputs/opportunities.json"))
    args = p.parse_args()
    if len(args.expected_sha256) != 64 or not all(c in "0123456789abcdef" for c in args.expected_sha256):
        raise ValueError("Expected an out-of-band SHA256 digest")
    actual = hashlib.sha256(args.model.read_bytes()).hexdigest()
    if actual != args.expected_sha256:
        raise ValueError("Checkpoint digest mismatch")
    verify_engine()
    import torch
    from sb3_contrib import MaskablePPO
    torch.set_num_threads(2)
    model = MaskablePPO.load(str(args.model), device="cpu")
    controls = [real_game(seed, "baseline") for seed in args.seeds]
    candidates = [real_game(seed, "model", model, actual) for seed in args.seeds]
    result = {
        "schema": 1, "session_id": SESSION,
        "model_sha256": actual,
        "seeds": args.seeds, "candidate": candidates, "baseline": controls,
        "candidate_summary": summary(candidates), "baseline_summary": summary(controls),
        "training_steps_this_run": 0,
        "caveat": "Model results with forced ends are guarded; never rank/promote as pure model.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"candidate": result["candidate_summary"],
                      "baseline": result["baseline_summary"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
