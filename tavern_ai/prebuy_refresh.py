"""One midgame refresh before the first legal purchase, real TavernGym only.

Round 002: disjoint from the round-001 non-activating end-turn refresh trigger.
No PPO gradients or synthetic matches.
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
from .canary import run as run_baseline
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION_ID = "s-20261102-6cc5d763"
POLICY_VERSION = "prebuy-refresh-v1"


class PreBuyRefreshPolicy:
    def __init__(self, min_turn: int = 4):
        if min_turn < 0:
            raise ValueError("min_turn cannot be negative")
        self.base = BaselinePolicy()
        self.min_turn = min_turn
        self.current_turn = None
        self.refreshes_this_turn = 0
        self.total_refreshes = 0
        self.opportunities = 0

    def act(self, obs: dict, turn: int, actions_used: int) -> int:
        mask = np.asarray(obs["action_mask"], dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise ValueError("Expected 245 legal-action flags")
        if turn != self.current_turn:
            self.current_turn = turn
            self.refreshes_this_turn = 0
        original = self.base.act(obs, {"turn": turn, "actions_used": actions_used})
        if (
            8 <= original <= 16
            and mask[1]  # Refresh
            and turn >= self.min_turn
            and actions_used < 70
        ):
            self.opportunities += 1
            if self.refreshes_this_turn == 0:
                self.refreshes_this_turn += 1
                self.total_refreshes += 1
                original = 1
        if not mask[original]:
            raise ValueError("Illegal action from refresh policy")
        return int(original)


def candidate_game(seed: int, agent_id: str = SESSION_ID) -> dict:
    import taverngym
    engine = verify_engine()
    game = taverngym.Game(seed=int(seed))
    policy = PreBuyRefreshPolicy()
    actions_this_turn, last_turn, decisions = 0, -1, 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if last_turn != turn:
            last_turn, actions_this_turn = turn, 0
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            features, cards = game.observe2(0)
            f = np.frombuffer(features, dtype="<f4").copy()
            c = np.frombuffer(cards, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Unexpected pinned observe2 observation")
            action = policy.act({"features": f, "cards": c, "action_mask": mask},
                                turn=turn, actions_used=actions_this_turn)
            if not mask[action]:
                raise ValueError("Candidate selected an illegal action")
            game.step(0, action)
            decisions += 1
            actions_this_turn += 1
        if not progress and not game.is_over():
            raise RuntimeError("Real engine stalled")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")
    receipt = {
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
        "placements": [int(v) for v in game.placements()],
        "refreshes_chosen": policy.total_refreshes,
        "refresh_opportunities": policy.opportunities,
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
    }
    validate(receipt)
    return receipt


def summary(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("Empty evaluation cohort")
    ranks = [r["placements"][0] for r in rows]
    return {
        "games": len(rows),
        "seeds": [r["seed"] for r in rows],
        "ranks": ranks,
        "mean_rank": sum(ranks) / len(ranks),
        "first_place_rate": sum(x == 1 for x in ranks) / len(ranks),
        "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
    }


def experiment(seed: int, start_seed: int, games: int,
               out_dir: Path, report_path: Path) -> dict:
    if not 1 <= games <= 8:
        raise ValueError("Only 1..8 bounded held-out games allowed")
    if start_seed <= seed < start_seed + games:
        raise ValueError("Mandatory canary seed must be disjoint")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    first = candidate_game(seed)
    (out_dir / f"002-{seed}.json").write_text(json.dumps(first, indent=2), encoding="utf-8")
    baseline, candidate = [], []
    for i in range(games):
        s = start_seed + i
        b = run_baseline(s, SESSION_ID, "baseline")
        c = candidate_game(s)
        baseline.append(b)
        candidate.append(c)
        (out_dir / f"r002-baseline-{s}.json").write_text(
            json.dumps(b, indent=2), encoding="utf-8")
        (out_dir / f"r002-candidate-{s}.json").write_text(
            json.dumps(c, indent=2), encoding="utf-8")
    bs, cs = summary(baseline), summary(candidate)
    refreshes = [first["refreshes_chosen"]] + [r["refreshes_chosen"] for r in candidate]
    report = {
        "session_id": SESSION_ID, "round": 2,
        "base_main": "315b068bac5ab6d8403c3c9b18f8c101c0cded5d",
        "engine_version": first["engine_version"],
        "engine_source_hash": first["engine_source_hash"],
        "policy": POLICY_VERSION, "policy_sha256": first["policy_sha256"],
        "ppo_training_steps": 0, "checkpoint": None,
        "mandatory": {
            "seed": seed, "rank": first["placements"][0],
            "decisions": first["decisions"], "turns": first["turns"],
            "refreshes_chosen": first["refreshes_chosen"],
            "completed": first["completed"],
            "receipt": f"experiments/{SESSION_ID}/002-{seed}.json",
        },
        "baseline": bs, "candidate": cs,
        "paired_rank_delta": [c["placements"][0] - b["placements"][0]
                              for b, c in zip(baseline, candidate)],
        "mean_rank_delta": cs["mean_rank"] - bs["mean_rank"],
        "refreshes_per_candidate_game": refreshes,
        "total_candidate_refreshes": sum(refreshes),
        "intervention_valid": sum(refreshes) > 0,
        "interpretation": "Small descriptive pilot; not evidence of strength improvement",
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if not report["intervention_valid"]:
        raise RuntimeError("Invalid ablation: zero refresh interventions; inspect receipts")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=36511)
    parser.add_argument("--start-seed", type=int, default=36512)
    parser.add_argument("--games", type=int, default=4)
    parser.add_argument("--out-dir", type=Path, default=Path(f"experiments/{SESSION_ID}"))
    parser.add_argument("--report", type=Path, default=Path(f"reports/{SESSION_ID}/round-002.json"))
    args = parser.parse_args()
    experiment(args.seed, args.start_seed, args.games, args.out_dir, args.report)

if __name__ == "__main__":
    main()
