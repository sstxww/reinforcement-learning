"""Isolated real-engine mask/observation recurrence probe; no policy changes."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import statistics

import numpy as np

from .baseline import BaselinePolicy
from .canary import run as baseline_canary
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate


def bucket(action: int) -> str:
    """Stable ID ranges: deliberately do not assume unverified action semantics."""
    if not 0 <= action < ACTIONS:
        raise ValueError("out-of-range action")
    for lower, upper in ((0, 8), (8, 16), (16, 30), (30, 46),
                         (46, 126), (126, 196), (196, 245)):
        if lower <= action < upper:
            return f"{lower:03d}-{upper-1:03d}"
    raise AssertionError("unreachable")


class MaskTrace:
    def __init__(self):
        self.choices: Counter[int] = Counter()
        self.buckets: Counter[str] = Counter()
        self.legal_counts: list[int] = []
        self.state_seen: Counter[tuple[int, str]] = Counter()
        self.actions_by_turn: Counter[int] = Counter()
        self.repeated_observations = 0

    def record(self, turn: int, features: bytes, cards: bytes,
               mask: np.ndarray, action: int) -> None:
        if mask.shape != (ACTIONS,) or mask.dtype != np.bool_ or not mask.any():
            raise ValueError("missing or malformed legal action mask")
        if not 0 <= action < ACTIONS or not bool(mask[action]):
            raise ValueError(f"illegal action {action}")
        if len(features) != 4 * FEATURES or len(cards) != 4 * CARDS:
            raise ValueError("unexpected observe2 byte layout")
        fingerprint = hashlib.sha256(
            features + cards + mask.astype(np.uint8).tobytes()
        ).hexdigest()[:24]
        key = (int(turn), fingerprint)
        self.repeated_observations += bool(self.state_seen[key])
        self.state_seen[key] += 1
        self.legal_counts.append(int(mask.sum()))
        self.choices[int(action)] += 1
        self.buckets[bucket(int(action))] += 1
        self.actions_by_turn[int(turn)] += 1

    def summarize(self) -> dict:
        return {
            "mask_checks": len(self.legal_counts),
            "minimum_legal_actions": min(self.legal_counts, default=0),
            "maximum_legal_actions": max(self.legal_counts, default=0),
            "mean_legal_actions": statistics.mean(self.legal_counts)
                if self.legal_counts else 0,
            "revisited_observations": self.repeated_observations,
            "max_identical_observation_visits": max(self.state_seen.values(), default=0),
            "max_own_decisions_in_turn": max(self.actions_by_turn.values(), default=0),
            "action_buckets": dict(sorted(self.buckets.items())),
            "action_ids": dict(sorted((str(k), v) for k, v in self.choices.items())),
        }


def run_probed_match(seed: int, agent_id: str) -> tuple[dict, dict]:
    """Seat 0 = unchanged BaselinePolicy; other seven = official engine bots."""
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=int(seed))
    baseline = BaselinePolicy()
    trace = MaskTrace()
    actions_this_turn = 0
    last_turn = -1
    decisions = 0
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
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            f = np.frombuffer(fbytes, dtype="<f4").copy()
            c = np.frombuffer(cbytes, dtype="<i4").copy()
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("unexpected observe2 shape")
            action = int(baseline.act(
                {"features": f, "cards": c, "action_mask": mask},
                {"turn": turn, "actions_used": actions_this_turn}
            ))
            trace.record(turn, fbytes, cbytes, mask, action)
            game.step(0, action)
            decisions += 1
            actions_this_turn += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")
    receipt = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"], "agent_id": agent_id,
        "policy": "baseline", "seed": int(seed), "completed": True,
        "turns": int(game.turn), "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""), "model_sha256": None,
        "trace": trace.summarize(),
    }
    validate(receipt)
    if receipt["trace"]["mask_checks"] != receipt["decisions"]:
        raise AssertionError("missing seat-0 mask checks")
    return receipt, receipt["trace"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--start-seed", type=int, default=48101)
    p.add_argument("--games", type=int, default=3)
    p.add_argument("--session-id", default="s-20261102-bd90a20b")
    p.add_argument("--receipt-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    if not 1 <= a.games <= 6:
        raise ValueError("games must be 1..6")
    if a.session_id != "s-20261102-bd90a20b":
        raise ValueError("probe must write only its own namespace")
    a.receipt_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in range(a.start_seed, a.start_seed + a.games):
        own, trace = run_probed_match(seed, a.session_id)
        baseline = baseline_canary(seed, a.session_id, "baseline")
        keys = ("placements", "decisions", "turns", "truncated_combats", "turn_limit_end")
        differences = {key: [own[key], baseline[key]]
                       for key in keys if own[key] != baseline[key]}
        own_path = a.receipt_dir / f"001-{seed}.json"
        base_path = a.receipt_dir / f"control-{seed}.json"
        own_path.write_text(json.dumps(own, indent=2), encoding="utf-8")
        base_path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
        rows.append({
            "seed": seed, "rank": own["placements"][0], "decisions": own["decisions"],
            "same_as_uninstrumented_baseline": not differences,
            "differences": differences, "mask_trace": trace,
            "receipt": str(own_path), "control_receipt": str(base_path),
        })
        if differences:
            raise AssertionError(f"instrumentation altered seeded game {seed}: {differences}")
    result = {
        "session_id": a.session_id, "study": "non-invasive mask recurrence diagnostics",
        "engine": verify_engine(), "policy": "original baseline; no new gameplay strategy",
        "training_steps": 0, "games": len(rows),
        "mean_rank": statistics.mean(r["rank"] for r in rows),
        "first_place_rate": sum(r["rank"] == 1 for r in rows) / len(rows),
        "top4_rate": sum(r["rank"] <= 4 for r in rows) / len(rows),
        "paired_replay_identical": all(r["same_as_uninstrumented_baseline"] for r in rows),
        "rows": rows, "competitive_improvement": "not tested",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
