"""Bounded shop refresh ablation against the unmodified V1 baseline.

Real TavernGym engine only; no replacement simulator. One controlled seat versus
seven built-in scripted bots. This does not train a PPO model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .canary import run as baseline_game
from .validate_receipt import validate

SESSION_ID = "s-20261102-6cc5d763"
POLICY_VERSION = "refresh-once-v1"


class RefreshOncePolicy:
    """Refresh once per turn if baseline would otherwise end, with no legal buys.

    The source TavernGym actions.rs maps 0=EndTurn, 1=Refresh and 8..16=Buy.
    All decisions remain subject to the actual engine legal-action mask.
    """

    def __init__(self, max_refreshes_per_turn: int = 1):
        if max_refreshes_per_turn < 0 or max_refreshes_per_turn > 2:
            raise ValueError("Refresh cap must be between 0 and 2")
        self._base = BaselinePolicy()
        self.cap = max_refreshes_per_turn
        self.turn = None
        self.used = 0
        self.total_refreshes = 0

    def act(self, observation: dict, turn: int, actions_used: int) -> int:
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise ValueError("Expected a nonempty 245-action mask")
        if turn != self.turn:
            self.turn = turn
            self.used = 0
        action = self._base.act(observation, {"turn": turn, "actions_used": actions_used})
        if (
            action == 0
            and turn >= 3
            and actions_used < 80
            and self.used < self.cap
            and mask[1]
            and not mask[8:17].any()
        ):
            self.used += 1
            self.total_refreshes += 1
            action = 1
        if not mask[action]:
            raise ValueError("Candidate emitted an illegal action")
        return int(action)


def run_candidate(seed: int, agent_id: str = SESSION_ID) -> dict:
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=int(seed))
    policy = RefreshOncePolicy()
    decisions, actions_this_turn, last_turn = 0, 0, -1
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
            floats, cards = game.observe2(0)
            f = np.frombuffer(floats, dtype="<f4").copy()
            c = np.frombuffer(cards, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("TavernGym observe2 contract mismatch")
            action = policy.act(
                {"features": f, "cards": c, "action_mask": mask},
                turn=turn,
                actions_used=actions_this_turn,
            )
            if not mask[action]:
                raise ValueError("Illegal candidate action")
            game.step(0, action)
            decisions += 1
            actions_this_turn += 1
        if not progress and not game.is_over():
            raise RuntimeError("Real TavernGym game stalled")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")

    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": agent_id,
        "policy": POLICY_VERSION,
        "policy_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "model_sha256": None,
        "seed": int(seed),
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(p) for p in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "refreshes_chosen": policy.total_refreshes,
        "git_sha": os.environ.get("GITHUB_SHA", ""),
    }
    validate(result)
    return result


def summarize(records: list[dict]) -> dict:
    if not records:
        raise ValueError("At least one completed game is required")
    places = [row["placements"][0] for row in records]
    return {
        "games": len(records),
        "seeds": [row["seed"] for row in records],
        "placements": places,
        "mean_placement": sum(places) / len(places),
        "first_place_rate": sum(p == 1 for p in places) / len(places),
        "top4_rate": sum(p <= 4 for p in places) / len(places),
    }


def execute(seed: int, start_seed: int, games: int, out_dir: Path, report_path: Path) -> dict:
    if not 1 <= games <= 10:
        raise ValueError("Bounded experiment requires 1..10 holdout games")
    if start_seed <= seed < start_seed + games:
        raise ValueError("Canary seed must be disjoint from held-out seeds")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    mandatory = run_candidate(seed)
    (out_dir / f"001-{seed}.json").write_text(json.dumps(mandatory, indent=2), encoding="utf-8")
    baseline_rows, candidate_rows = [], []
    for i in range(games):
        test_seed = start_seed + i
        original = baseline_game(test_seed, SESSION_ID, "baseline")
        candidate = run_candidate(test_seed)
        baseline_rows.append(original)
        candidate_rows.append(candidate)
        (out_dir / f"baseline-{test_seed}.json").write_text(
            json.dumps(original, indent=2), encoding="utf-8")
        (out_dir / f"candidate-{test_seed}.json").write_text(
            json.dumps(candidate, indent=2), encoding="utf-8")
    b, c = summarize(baseline_rows), summarize(candidate_rows)
    report = {
        "session_id": SESSION_ID,
        "hypothesis": "A single legal refresh when no buy is possible improves game placement",
        "main_base_sha": "315b068bac5ab6d8403c3c9b18f8c101c0cded5d",
        "engine_version": mandatory["engine_version"],
        "engine_hash": mandatory["engine_source_hash"],
        "policy_version": POLICY_VERSION,
        "policy_sha256": mandatory["policy_sha256"],
        "ppo_training_steps": 0,
        "candidate_canary": {
            "seed": seed,
            "rank": mandatory["placements"][0],
            "decisions": mandatory["decisions"],
            "refreshes": mandatory["refreshes_chosen"],
            "receipt": f"experiments/{SESSION_ID}/001-{seed}.json",
        },
        "baseline": b,
        "candidate": c,
        "paired_rank_deltas": [
            candidate["placements"][0] - original["placements"][0]
            for original, candidate in zip(baseline_rows, candidate_rows)
        ],
        "mean_rank_delta_candidate_minus_baseline": c["mean_placement"] - b["mean_placement"],
        "refresh_counts": [r["refreshes_chosen"] for r in candidate_rows],
        "conclusion": "Descriptive pilot only; small sample cannot establish improvement",
        "model_checkpoint": None,
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=36501)
    parser.add_argument("--start-seed", type=int, default=36502)
    parser.add_argument("--games", type=int, default=3)
    parser.add_argument("--out-dir", type=Path, default=Path(f"experiments/{SESSION_ID}"))
    parser.add_argument("--report", type=Path, default=Path(f"reports/{SESSION_ID}/comparison.json"))
    args = parser.parse_args()
    execute(args.seed, args.start_seed, args.games, args.out_dir, args.report)


if __name__ == "__main__":
    main()
