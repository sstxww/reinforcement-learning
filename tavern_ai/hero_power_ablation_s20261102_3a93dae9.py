"""Session-local, real-TavernGym free hero-power ablation. Never used in ranked play."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from tavern_ai.baseline import BaselinePolicy
from tavern_ai.canary import run as run_baseline
from tavern_ai.contract import ACTIONS, CARDS, FEATURES, PATCH_SHA256, UPSTREAM_COMMIT, verify_engine
from tavern_ai.validate_receipt import validate

SESSION_ID = "s-20261102-3a93dae9"
SEEDS = (18021, 18022)


class FreeHeroPowerPolicy:
    """Ablate one free hero power per turn; otherwise use unchanged V0 baseline."""

    def __init__(self):
        self.baseline = BaselinePolicy()
        self.turn = None
        self.used_this_turn = False
        self.hero_actions = 0

    def act(self, observation: dict, context: dict) -> int:
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise ValueError("Expected nonempty 245-action mask")
        turn = int(context.get("turn", 0))
        if self.turn != turn:
            self.turn, self.used_this_turn = turn, False

        # Every outstanding hero selection, Discover or target choice blocks ordinary actions.
        if mask[30:46].any():
            return self.baseline.act(observation, context)
        if not self.used_this_turn:
            f = np.asarray(observation["features"], dtype=np.float32)
            if f.shape != (FEATURES,):
                raise ValueError("Unexpected observe2 feature layout")
            # Pinned upstream obs.rs: hero-power prices at feature indices 17 and 20,
            # divided by five; legal mask at actions 4 and 5 guards target availability.
            for action, price_index in ((4, 17), (5, 20)):
                if mask[action] and np.isfinite(f[price_index]) and f[price_index] == 0:
                    self.used_this_turn = True
                    self.hero_actions += 1
                    return action
        return self.baseline.act(observation, context)


def run_candidate(seed: int, agent_id: str = SESSION_ID) -> dict:
    import taverngym

    if agent_id != SESSION_ID:
        raise ValueError("Session identity mismatch")
    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    policy = FreeHeroPowerPolicy()
    decisions = 0
    actions_this_turn = 0
    last_turn = -1
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
            fbytes, cbytes = game.observe2(0)
            floats = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if floats.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Pinned observe2 contract violated")
            action = int(policy.act(
                {"features": floats, "cards": cards, "action_mask": mask},
                {"turn": turn, "actions_used": actions_this_turn},
            ))
            if not mask[action]:
                raise ValueError(f"Illegal candidate action {action}")
            game.step(0, action)
            actions_this_turn += 1
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")

    payload = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "upstream_commit": UPSTREAM_COMMIT,
        "observe2_patch_sha256": PATCH_SHA256,
        "agent_id": agent_id,
        "policy": "free_hero_power_once_per_turn",
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(p) for p in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": None,
        "policy_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "hero_power_actions": policy.hero_actions,
        "illegal_actions": 0,
        "game_is_over": bool(game.is_over()),
    }
    validate(payload)
    return payload


def summary(records: list[dict]) -> dict:
    placements = [int(r["placements"][0]) for r in records]
    return {
        "n": len(placements),
        "placements": placements,
        "mean_placement": sum(placements) / len(placements),
        "top4_rate": sum(p <= 4 for p in placements) / len(placements),
        "first_place_rate": sum(p == 1 for p in placements) / len(placements),
    }


def run_paired(seeds: tuple[int, ...] = SEEDS, out_root: Path | None = None) -> dict:
    root = out_root or Path("experiments") / SESSION_ID
    root.mkdir(parents=True, exist_ok=True)
    candidate, baseline = [], []
    for seed in seeds:
        # The candidate itself must first finish a genuine eight-player game.
        c = run_candidate(seed)
        (root / f"001-{seed}.json").write_text(
            json.dumps(c, indent=2), encoding="utf-8")
        b = run_baseline(seed, SESSION_ID, "baseline")
        (root / f"baseline-{seed}.json").write_text(
            json.dumps(b, indent=2), encoding="utf-8")
        candidate.append(c)
        baseline.append(b)
    result = {
        "session_id": SESSION_ID,
        "hypothesis": "Use one zero-cost legal hero power per turn before baseline shop actions",
        "seeds": list(seeds),
        "candidate": summary(candidate),
        "baseline": summary(baseline),
        "hero_power_actions_per_game": [x["hero_power_actions"] for x in candidate],
        "paired_mean_placement_delta": (
            summary(candidate)["mean_placement"] - summary(baseline)["mean_placement"]
        ),
        "interpretation": "Exploratory sample; no validated strength improvement claimed",
    }
    report = Path("research") / "sessions" / SESSION_ID / "paired-results.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, nargs="+", default=SEEDS)
    args = parser.parse_args()
    if len(args.seeds) < 1 or len(set(args.seeds)) != len(args.seeds):
        parser.error("Seeds must be nonempty and distinct")
    print(json.dumps(run_paired(tuple(args.seeds)), ensure_ascii=False))


if __name__ == "__main__":
    main()
