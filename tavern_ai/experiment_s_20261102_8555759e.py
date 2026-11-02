"""Isolated matched-seed real-engine ablation of legal discover/choice priority.

This experiment only changes the tie-break inside actions 30..45. Every
other decision is delegated to the repository's current BaselinePolicy.
No arena connections, no synthetic game results, and no external checkpoints.
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

from tavern_ai.baseline import BaselinePolicy
from tavern_ai.contract import ACTIONS, CARDS, FEATURES, verify_engine
from tavern_ai.validate_receipt import validate

SESSION = "s-20261102-8555759e"
FIRST_CHOICE, AFTER_CHOICE = 30, 46
DEFAULT_SEED = 855570


class LastChoicePolicy:
    """Use highest-index legal choice; otherwise follow the unchanged baseline."""

    def __init__(self):
        self.baseline = BaselinePolicy()

    def act(self, observation: dict, context: dict | None = None) -> int:
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise ValueError("Expected nonempty 245-action legal mask")
        options = np.flatnonzero(mask[FIRST_CHOICE:AFTER_CHOICE])
        if len(options):
            return FIRST_CHOICE + int(options[-1])
        return self.baseline.act(observation, context)


def choice_candidates(mask: np.ndarray) -> np.ndarray:
    return np.flatnonzero(mask[FIRST_CHOICE:AFTER_CHOICE]) + FIRST_CHOICE


def play_game(seed: int, candidate: bool) -> dict:
    """Run until real Game.is_over() without modifying TavernGym internals."""
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    policy = LastChoicePolicy() if candidate else BaselinePolicy()
    decisions = 0
    last_turn = -1
    actions_this_turn = 0
    choice_actions = 0
    multi_choice_actions = 0
    alternative_choices = 0
    illegal_actions = 0

    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, actions_this_turn = turn, 0

        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue

            float_bytes, card_bytes = game.observe2(0)
            features = np.frombuffer(float_bytes, dtype="<f4").copy()
            cards = np.frombuffer(card_bytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Unexpected TavernGym observe2 contract")
            if not np.isfinite(features).all():
                raise ValueError("Nonfinite feature observations")
            if not mask.any():
                raise ValueError("No legal action")

            observation = {"features": features, "cards": cards, "action_mask": mask}
            context = {"turn": turn, "actions_used": actions_this_turn}
            options = choice_candidates(mask)
            action = int(policy.act(observation, context))
            if len(options):
                choice_actions += 1
                if len(options) > 1:
                    multi_choice_actions += 1
                if action != int(options[0]):
                    alternative_choices += 1
            if action < 0 or action >= ACTIONS or not mask[action]:
                illegal_actions += 1
                raise ValueError(f"Illegal action {action} in seed {seed}")

            game.step(0, action)
            decisions += 1
            actions_this_turn += 1

        if not progressed and not game.is_over():
            raise RuntimeError(f"Game stalled at turn {game.turn}")

    if not game.is_over():
        raise RuntimeError(f"Full-game safety limit exceeded for seed {seed}")

    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": SESSION,
        "policy": "discover-last-v1" if candidate else "baseline-first-choice",
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "illegal_actions": illegal_actions,
        "choice_actions": choice_actions,
        "multi_choice_actions": multi_choice_actions,
        "alternative_choices": alternative_choices,
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "policy_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "model_sha256": None,
    }
    validate(result)
    return result


def summarize(records: list[dict]) -> dict:
    ranks = [r["placements"][0] for r in records]
    return {
        "games": len(ranks),
        "mean_placement": statistics.mean(ranks),
        "first_place_rate": sum(rank == 1 for rank in ranks) / len(ranks),
        "top4_rate": sum(rank <= 4 for rank in ranks) / len(ranks),
        "placements": ranks,
        "seeds": [r["seed"] for r in records],
        "total_choice_actions": sum(r["choice_actions"] for r in records),
        "total_multi_choice_actions": sum(r["multi_choice_actions"] for r in records),
        "total_alternative_choices": sum(r["alternative_choices"] for r in records),
    }


def run_experiment(start_seed: int, games: int, output_root: Path, report_path: Path) -> dict:
    if not 1 <= games <= 30:
        raise ValueError("games must be 1..30 for bounded experiments")
    output_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_records, candidate_records = [], []

    for seed in range(start_seed, start_seed + games):
        baseline = play_game(seed, candidate=False)
        candidate = play_game(seed, candidate=True)
        baseline_records.append(baseline)
        candidate_records.append(candidate)
        for label, record in (("baseline", baseline), ("001", candidate)):
            target = output_root / f"{label}-{seed}.json"
            target.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({
            "seed": seed,
            "baseline_rank": baseline["placements"][0],
            "candidate_rank": candidate["placements"][0],
            "candidate_choices": candidate["choice_actions"],
            "candidate_alternative_choices": candidate["alternative_choices"],
            "completed_both": True,
        }), flush=True)

    paired_deltas = [a["placements"][0] - b["placements"][0]
                     for a, b in zip(candidate_records, baseline_records)]
    report = {
        "session": SESSION,
        "experiment": "first legal choice vs last legal choice in action indices 30..45",
        "hypothesis": "The default first-choice tie-break introduces systematic choice-index bias",
        "environment": "real pinned TavernGym 1.1.0 eight-seat matches",
        "model_training_steps": 0,
        "policy_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "baseline": summarize(baseline_records),
        "candidate": summarize(candidate_records),
        "paired_rank_deltas_candidate_minus_baseline": paired_deltas,
        "mean_paired_rank_delta": statistics.mean(paired_deltas),
        "independent_seed_count": games,
        "inferential_warning": "Exploratory descriptive comparison. Small N, seeded opponents; no claim of superior strength.",
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--games", type=int, default=6)
    parser.add_argument("--out-dir", type=Path, default=Path(f"experiments/{SESSION}"))
    parser.add_argument("--report", type=Path, default=Path(f"reports/{SESSION}/round-001.json"))
    args = parser.parse_args()
    run_experiment(args.start_seed, args.games, args.out_dir, args.report)


if __name__ == "__main__":
    main()
