"""Isolated hero-power end-turn ablation on genuine TavernGym eight-seat games.

Control: the untouched V0 BaselinePolicy.
Candidate: if control would EndTurn, use one legal hero power per turn, then resume control.
No PPO model or weights are used, and this is not a trained strategy.
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


class IdleHeroPowerPolicy(BaselinePolicy):
    def __init__(self) -> None:
        self._last_turn: int | None = None
        self._used_this_turn = False
        self.hero_power_uses = 0

    def act(self, observation: dict, context: dict | None = None) -> int:
        context = context or {}
        turn = int(context.get("turn", 0))
        if turn != self._last_turn:
            self._last_turn = turn
            self._used_this_turn = False
        control = super().act(observation, context)
        # Never override a buy, play, choice, upgrade, or the baseline safety stop.
        if control != 0 or self._used_this_turn or int(context.get("actions_used", 0)) >= 60:
            return control
        mask = np.asarray(observation["action_mask"], dtype=bool)
        for hero_action in (4, 5):
            if mask[hero_action]:
                self._used_this_turn = True
                self.hero_power_uses += 1
                return hero_action
        return control


def run_game(seed: int, agent_id: str, candidate: bool) -> dict:
    import taverngym

    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("Invalid session agent id")
    engine = verify_engine()
    game = taverngym.Game(seed=int(seed))
    policy = IdleHeroPowerPolicy() if candidate else BaselinePolicy()
    turns_seen = -1
    actions_this_turn = 0
    decisions = 0
    illegal_actions = 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != turns_seen:
            turns_seen, actions_this_turn = turn, 0
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
                raise ValueError("Pinned observe2 dimensions mismatch")
            if not np.isfinite(features).all() or not mask.any():
                raise ValueError("Invalid observation or no legal action")
            action = int(policy.act(
                {"features": features, "cards": cards, "action_mask": mask},
                {"turn": turn, "actions_used": actions_this_turn},
            ))
            if not 0 <= action < ACTIONS or not mask[action]:
                illegal_actions += 1
                raise ValueError(f"Illegal policy action {action} at turn {turn}")
            game.step(0, action)
            decisions += 1
            actions_this_turn += 1
        if not progressed and not game.is_over():
            raise RuntimeError("Game stalled before terminal state")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded (NOT a successful match)")
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": agent_id,
        "policy": "idle-hero-power" if candidate else "baseline",
        "seed": int(seed),
        "completed": bool(game.is_over()),
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "illegal_actions": illegal_actions,
        "hero_power_uses": policy.hero_power_uses if candidate else 0,
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": None,
        "training_steps": 0,
        "workflow_run_url": (
            f"{os.getenv('GITHUB_SERVER_URL')}/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/"
            f"{os.getenv('GITHUB_RUN_ID')}"
            if os.getenv("GITHUB_RUN_ID") else None
        ),
    }
    validate(result)
    if len(set(result["placements"])) != 8:
        raise ValueError("Non-distinct final placements")
    return result


def summarize(rows: list[dict]) -> dict:
    ranks = [x["placements"][0] for x in rows]
    return {
        "games": len(ranks),
        "mean_placement": statistics.mean(ranks),
        "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
        "first_place_rate": sum(x == 1 for x in ranks) / len(ranks),
        "placements": ranks,
        "seeds": [r["seed"] for r in rows],
        "total_hero_power_uses": sum(x["hero_power_uses"] for x in rows),
    }


def benchmark(start_seed: int, games: int, agent_id: str, output_dir: Path, report_file: Path) -> dict:
    if not 1 <= games <= 12:
        raise ValueError("games must be 1..12")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    control, candidate = [], []
    for seed in range(start_seed, start_seed + games):
        # Baseline and candidate receive identical game seeds, seats and opponent bots.
        b = run_game(seed, agent_id, candidate=False)
        (output_dir / f"001-control-{seed}.json").write_text(json.dumps(b, indent=2), encoding="utf-8")
        c = run_game(seed, agent_id, candidate=True)
        (output_dir / f"001-{seed}.json").write_text(json.dumps(c, indent=2), encoding="utf-8")
        control.append(b)
        candidate.append(c)
        print(f"SEED {seed}: baseline={b['placements'][0]} candidate={c['placements'][0]} "
              f"power_uses={c['hero_power_uses']}", flush=True)
    base_summary, cand_summary = summarize(control), summarize(candidate)
    report = {
        "session_id": agent_id,
        "hypothesis": "One legal hero power only when baseline would EndTurn",
        "engine_source_hash": control[0]["engine_source_hash"],
        "baseline": base_summary,
        "candidate": cand_summary,
        "paired_placement_deltas": [
            c["placements"][0] - b["placements"][0] for b, c in zip(control, candidate)
        ],
        "mean_placement_delta": cand_summary["mean_placement"] - base_summary["mean_placement"],
        "claim": "Exploratory: not evidence of competitive improvement",
        "model_checkpoint": None,
        "training_steps": 0,
    }
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--agent-id", required=True)
    p.add_argument("--start-seed", type=int, default=73101)
    p.add_argument("--games", type=int, default=4)
    p.add_argument("--receipts", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    benchmark(a.start_seed, a.games, a.agent_id, a.receipts, a.report)


if __name__ == "__main__":
    main()
