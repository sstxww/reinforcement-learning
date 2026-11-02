"""V6.1 isolated, unassisted model economic-liveness probe.

This is diagnostic-only, not a policy fallback, score, or training run.
Never invent a placement when the complete eight-seat game did not finish.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION = "s-20261103-9dc0a960"
BUY_IDS = range(8, 16)


class RawActions:
    def __init__(self):
        self.counts = Counter()
        self.raw_ids = Counter()
        self.first = []
        self.last_turn = None
        self.last_public_state = None

    def observe(self, *, turn: int, mask, action: int, state_sha256: str) -> None:
        if len(mask) != ACTIONS or not any(mask):
            raise ValueError("Invalid or empty action mask")
        if not isinstance(action, int) or action < 0 or action >= ACTIONS or not bool(mask[action]):
            raise ValueError("Illegal raw model action")
        if not isinstance(state_sha256, str) or len(state_sha256) != 64:
            raise ValueError("Invalid public state digest")
        buy_legal = any(bool(mask[i]) for i in BUY_IDS)
        self.counts["decisions"] += 1
        self.counts["buy_legal_decision_exposures"] += int(buy_legal)
        self.counts["buy_actions"] += int(action in BUY_IDS)
        self.counts["end_turn_with_buy_legal"] += int(action == 0 and buy_legal)
        self.counts["end_turn"] += int(action == 0)
        self.counts["play_band"] += int(46 <= action < 126)
        self.counts["upgrade_action_3"] += int(action == 3)
        if self.last_turn == turn and self.last_public_state == state_sha256:
            self.counts["unchanged_public_obs_between_decisions"] += 1
        self.last_turn = turn
        self.last_public_state = state_sha256
        self.raw_ids[str(action)] += 1
        if len(self.first) < 64:
            self.first.append({
                "turn": turn, "raw_action_id": action,
                "buy_legal": buy_legal, "public_observation_sha256": state_sha256
            })

    def as_dict(self):
        exposures = self.counts["buy_legal_decision_exposures"]
        return {
            "counts": dict(self.counts),
            "raw_action_histogram": dict(self.raw_ids),
            "first_64_decisions": self.first,
            "buy_given_legal_exposure": (
                self.counts["buy_actions"] / exposures if exposures else None
            ),
            "denominator": (
                "One exposure is one own-seat decision with at least one mask-legal "
                "BUY ID (8..15); repeated exposures are correlated. Gold and "
                "affordability are NOT inferred independently from mask legality."
            ),
            "public_state_note": (
                "Hash is SHA256(public observe2 feature bytes + card bytes + legal mask). "
                "Repeated digest compares successive model decisions in the same turn, "
                "not internal engine states or hidden information."
            ),
        }


def probe(model_path: Path, seed: int, max_decisions: int) -> tuple[dict, dict | None]:
    if max_decisions < 1 or max_decisions > 2000:
        raise ValueError("max_decisions must be 1..2000")
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    import numpy as np
    import taverngym
    import torch
    from sb3_contrib import MaskablePPO

    torch.set_num_threads(1)
    engine = verify_engine()
    model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    stats = RawActions()
    stop_reason = None
    last_turn = None
    per_turn = 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, per_turn = turn, 0
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            if stats.counts["decisions"] >= max_decisions:
                stop_reason = "raw_model_decision_budget"
                break
            if per_turn >= 120:
                stop_reason = "raw_model_turn_liveness_budget"
                break
            fbytes, cbytes = game.observe2(0)
            features = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned public observation dimensions differ")
            if not np.isfinite(features).all():
                raise ValueError("Non-finite public features")
            state_hash = hashlib.sha256(fbytes + cbytes + mask.tobytes()).hexdigest()
            raw, _ = model.predict(
                {"features": features, "cards": cards},
                action_masks=mask, deterministic=True
            )
            action = int(np.asarray(raw).item())
            stats.observe(turn=turn, mask=mask, action=action, state_sha256=state_hash)
            game.step(0, action)
            per_turn += 1
        if stop_reason:
            break
        if not progress and not game.is_over():
            stop_reason = "engine_stalled"
            break
    complete = bool(game.is_over())
    if not complete and stop_reason is None:
        stop_reason = "engine_loop_budget"
    report = {
        "schema": "v61-raw-economic-liveness-1",
        "session_id": SESSION, "policy_mode": "unassisted_raw_maskable_ppo",
        "seed": seed, "controlled_seat": 0, "engine": engine,
        "checkpoint_sha256": model_hash,
        "completed": complete, "stop_reason": stop_reason,
        "game_turn": int(game.turn), "max_raw_model_decisions": max_decisions,
        "stats": stats.as_dict(),
        "placement": int(game.placements()[0]) if complete else None,
        "interpretation_limit": (
            "Exploratory one-seed raw-model behavior. Not evidence of causal defect "
            "or strength, and never counted as a completed game if incomplete."
        ),
    }
    receipt = None
    if complete:
        receipt = {
            "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": "TavernGym",
            "engine_version": engine["version"],
            "engine_source_hash": engine["source_hash"],
            "agent_id": SESSION, "policy": "model",
            "seed": seed, "completed": True, "turns": int(game.turn),
            "decisions": stats.counts["decisions"],
            "placements": [int(x) for x in game.placements()],
            "truncated_combats": int(game.truncated_combats),
            "turn_limit_end": bool(game.turn_limit_end),
            "model_sha256": model_hash,
            "raw_model_only": True, "guard_forced_ends": 0,
            "fallback_actions": 0,
        }
        validate(receipt)
    return report, receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=43837)
    parser.add_argument("--max-decisions", type=int, default=480)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    report, receipt = probe(args.model, args.seed, args.max_decisions)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if receipt is not None:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps({
        "completed": report["completed"], "stop_reason": report["stop_reason"],
        "checkpoint_sha256": report["checkpoint_sha256"],
        "stats": report["stats"]["counts"], "receipt_written": receipt is not None
    }))
    # Incomplete raw policies are evidence, not a successful complete-match gate.
    if not report["completed"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
