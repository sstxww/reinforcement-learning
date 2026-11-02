"""Session-isolated purchase-before-play priority ablation on real TavernGym.

No changes to the shared baseline; only the conditional action ordering changes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION_ID = "s-20261102-64405d5e"


class PurchaseBeforePlay:
    """Prefer a legal shop purchase only when baseline would play a hand card."""

    def __init__(self) -> None:
        self.baseline = BaselinePolicy()

    def act(self, observation: dict, context: dict | None = None) -> tuple[int, bool]:
        ctx = context or {}
        default = self.baseline.act(observation, ctx)
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if (46 <= default < 126 and int(ctx.get("actions_used", 0)) < 85):
            purchases = np.flatnonzero(mask[8:16])
            if len(purchases):
                alternative = 8 + int(purchases[0])
                return alternative, alternative != default
        return default, False


def run_match(seed: int, candidate: bool) -> dict:
    """Drive seat zero until Game.is_over, leaving all seven opponent bots intact."""
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=int(seed))
    probe = PurchaseBeforePlay()
    decisions = 0
    interventions = 0
    last_turn = -1
    actions_this_turn = 0
    max_actions_this_turn = 0
    histogram = {"choice": 0, "play": 0, "buy": 0, "other": 0}
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, actions_this_turn = turn, 0
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            features_b, cards_b = game.observe2(0)
            observation = {
                "features": np.frombuffer(features_b, dtype="<f4").copy(),
                "cards": np.frombuffer(cards_b, dtype="<i4").copy(),
                "action_mask": np.frombuffer(
                    game.legal_mask(0), dtype=np.uint8
                ).astype(bool),
            }
            if (
                observation["features"].shape != (FEATURES,)
                or observation["cards"].shape != (CARDS,)
                or observation["action_mask"].shape != (ACTIONS,)
            ):
                raise ValueError("Unexpected pinned observe2 contract")
            context = {"turn": turn, "actions_used": actions_this_turn}
            if candidate:
                action, intervened = probe.act(observation, context)
                interventions += int(intervened)
            else:
                action = probe.baseline.act(observation, context)
            if not observation["action_mask"][action]:
                raise ValueError(f"Illegal action: {action}")
            if 30 <= action < 46:
                histogram["choice"] += 1
            elif 46 <= action < 126:
                histogram["play"] += 1
            elif 8 <= action < 16:
                histogram["buy"] += 1
            else:
                histogram["other"] += 1
            game.step(0, int(action))
            actions_this_turn += 1
            max_actions_this_turn = max(max_actions_this_turn, actions_this_turn)
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled before completion")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION_ID,
        "policy": "purchase_before_play" if candidate else "baseline",
        "policy_sha256": source_hash if candidate else None,
        "model_sha256": None,
        "seed": int(seed),
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(p) for p in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "interventions": interventions,
        "action_histogram": histogram,
        "max_actions_this_turn": max_actions_this_turn,
        "git_sha": os.getenv("GITHUB_SHA", ""),
    }
    validate(receipt)
    if sorted(receipt["placements"]) != list(range(1, 9)):
        raise ValueError("Placements are not a complete ranking permutation")
    return receipt


def record(record_path: Path, data: dict) -> None:
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def experiment(seed: int, paired_seed: int, pairs: int, out_dir: Path, report_path: Path) -> dict:
    if not 1 <= pairs <= 20:
        raise ValueError("pairs must be in 1..20")
    primary = run_match(seed, candidate=True)
    record(out_dir / f"001-{seed}.json", primary)
    baseline_ranks = []
    candidate_ranks = []
    paired_records = []
    for offset in range(pairs):
        s = paired_seed + offset
        control = run_match(s, candidate=False)
        candidate = run_match(s, candidate=True)
        record(out_dir / "controls" / f"001-{s}.json", control)
        record(out_dir / f"001-{s}.json", candidate)
        baseline_ranks.append(control["placements"][0])
        candidate_ranks.append(candidate["placements"][0])
        paired_records.append({
            "seed": s,
            "baseline_rank": control["placements"][0],
            "candidate_rank": candidate["placements"][0],
            "candidate_interventions": candidate["interventions"],
            "baseline_decisions": control["decisions"],
            "candidate_decisions": candidate["decisions"],
        })
    metric = {
        "session_id": SESSION_ID,
        "hypothesis": "buy-before-play when both actions legal",
        "main_game_seed": seed,
        "main_game_rank": primary["placements"][0],
        "main_game_completed": primary["completed"],
        "main_game_interventions": primary["interventions"],
        "pairs": pairs,
        "baseline_mean_rank": statistics.mean(baseline_ranks),
        "candidate_mean_rank": statistics.mean(candidate_ranks),
        "paired_mean_rank_delta": statistics.mean(
            c - b for c, b in zip(candidate_ranks, baseline_ranks)
        ),
        "baseline_top4_rate": sum(r <= 4 for r in baseline_ranks) / pairs,
        "candidate_top4_rate": sum(r <= 4 for r in candidate_ranks) / pairs,
        "baseline_first_rate": sum(r == 1 for r in baseline_ranks) / pairs,
        "candidate_first_rate": sum(r == 1 for r in candidate_ranks) / pairs,
        "total_candidate_interventions": sum(r["candidate_interventions"] for r in paired_records),
        "paired_games": paired_records,
        "engine_version": primary["engine_version"],
        "engine_source_hash": primary["engine_source_hash"],
        "model_training_steps": 0,
        "interpretation": "Exploratory; do not claim strength gain from a small sample.",
    }
    record(report_path, metric)
    print(json.dumps(metric, ensure_ascii=False))
    return metric


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=41060)
    p.add_argument("--paired-seed", type=int, default=41061)
    p.add_argument("--pairs", type=int, default=6)
    p.add_argument("--out-dir", type=Path, default=Path("experiments") / SESSION_ID)
    p.add_argument("--report", type=Path, default=Path("reports") / SESSION_ID / "paired-001.json")
    args = p.parse_args()
    experiment(args.seed, args.paired_seed, args.pairs, args.out_dir, args.report)


if __name__ == "__main__":
    main()
