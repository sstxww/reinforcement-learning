"""Isolated pinned-engine PPO behavior audit, honest about fallback.

Raw probe is NOT a completed-game receipt unless Game.is_over().
Guarded matches use a forced legal END_TURN and are never pure PPO.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics

import numpy as np

from .canary import run as baseline_game
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION = "s-20261102-880b8a71"
GUARD_LIMIT = 36
RAW_PROBE_BUDGET = 600


def category(action: int) -> str:
    if action == 0:
        return "end_turn"
    if action == 3:
        return "upgrade"
    if 8 <= action <= 15:
        return "buy"
    if 16 <= action <= 29:
        return "shop_or_sell"
    if 30 <= action <= 45:
        return "choose"
    if 46 <= action <= 125:
        return "play"
    return "other"


def decide(mask: np.ndarray, proposed: int, used: int,
           guard_limit: int | None) -> tuple[int, bool]:
    if mask.shape != (ACTIONS,) or not mask.any():
        raise ValueError("Empty or malformed legal-action mask")
    if proposed < 0 or proposed >= ACTIONS or not bool(mask[proposed]):
        raise ValueError("Illegal raw model proposal")
    if guard_limit is not None and used >= guard_limit and mask[0]:
        return 0, True
    return proposed, False


def one_game(seed: int, model, model_sha: str, engine: dict,
             guard_limit: int | None, own_action_limit: int = 600) -> tuple[dict, dict | None]:
    import taverngym
    game = taverngym.Game(seed=seed)
    histogram = Counter()
    legal_opportunities = Counter()
    selected_when_buy_legal = Counter()
    changes = Counter()
    turns = Counter()
    last_turn = None
    per_turn_actions = 0
    previous_observation = None
    previous_turn = None
    raw_actions = 0
    forced_ends = 0
    model_chosen_ends = 0
    first_actions = []
    stop_reason = None
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, per_turn_actions = turn, 0
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
                raise ValueError("TavernGym public-observation contract changed")
            if not np.isfinite(features).all():
                raise ValueError("Nonfinite public features")
            obs_hash = hashlib.sha256(fbytes + cbytes + mask.tobytes()).hexdigest()
            if previous_turn == turn:
                changes["consecutive_observation_pairs"] += 1
                if obs_hash == previous_observation:
                    changes["same_public_observation_as_previous"] += 1
            previous_observation, previous_turn = obs_hash, turn
            raw, _ = model.predict({"features": features, "cards": cards},
                                   action_masks=mask, deterministic=True)
            raw_action = int(np.asarray(raw).item())
            action, was_forced = decide(mask, raw_action, per_turn_actions, guard_limit)
            if bool(mask[8:16].any()):
                legal_opportunities["decisions_with_legal_buy"] += 1
                selected_when_buy_legal[category(action)] += 1
            legal_opportunities["own_decisions"] += 1
            legal_opportunities["legal_end_turn_opportunities"] += int(mask[0])
            histogram[category(action)] += 1
            turns[str(turn)] += 1
            if len(first_actions) < 32:
                first_actions.append({"turn": turn, "chosen": action,
                                      "raw": raw_action, "buy_legal": bool(mask[8:16].any()),
                                      "forced": was_forced})
            forced_ends += int(was_forced)
            model_chosen_ends += int(raw_action == 0 and not was_forced)
            game.step(0, action)
            raw_actions += 1
            per_turn_actions += 1
            if raw_actions >= own_action_limit and not game.is_over():
                stop_reason = "own_action_audit_budget_exhausted"
                break
        if stop_reason:
            break
        if not progressed and not game.is_over():
            raise RuntimeError("Actual TavernGym game stopped making progress")
    if not game.is_over() and not stop_reason:
        stop_reason = "engine_iteration_safety_limit"
    summary = {
        "seed": seed, "completed": bool(game.is_over()),
        "stop_reason": stop_reason,
        "game_turn": int(game.turn),
        "raw_model_actions": raw_actions, "model_chosen_ends": model_chosen_ends,
        "guard_forced_ends": forced_ends,
        "guard_limit_per_turn": guard_limit, "action_category_counts": dict(histogram),
        "legal_action_opportunities": dict(legal_opportunities),
        "choice_when_buy_legal": dict(selected_when_buy_legal),
        "observation_progress": dict(changes), "per_turn_decisions": dict(turns),
        "first_actions": first_actions,
    }
    receipt = None
    if game.is_over():
        receipt = {
            "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": "TavernGym", "engine_version": engine["version"],
            "engine_source_hash": engine["source_hash"],
            "agent_id": SESSION,
            "policy": "guarded_model" if guard_limit is not None else "model",
            "model_sha256": model_sha, "seed": seed, "completed": True,
            "turns": int(game.turn), "decisions": raw_actions,
            "placements": [int(x) for x in game.placements()],
            "truncated_combats": int(game.truncated_combats),
            "turn_limit_end": bool(game.turn_limit_end),
            "guard_forced_ends": forced_ends, "model_chosen_end_turns": model_chosen_ends,
            "raw_model_only": guard_limit is None,
        }
        validate(receipt)
        if sorted(receipt["placements"]) != list(range(1, 9)):
            raise ValueError("Non-permutation final placements")
        summary["rank"] = receipt["placements"][0]
    return summary, receipt


def audit(model_path: Path, out_dir: Path, report_path: Path,
          canary_seed: int = 23051, paired_seeds: tuple[int, ...] = (27100, 27101, 27102)) -> dict:
    from sb3_contrib import MaskablePPO
    import torch
    torch.set_num_threads(1)
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    engine = verify_engine()
    sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
    model = MaskablePPO.load(str(model_path), device="cpu")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    raw, raw_receipt = one_game(canary_seed, model, sha, engine, None, RAW_PROBE_BUDGET)
    if raw_receipt is not None:
        (out_dir / f"raw-{canary_seed}.json").write_text(json.dumps(raw_receipt, indent=2) + "\n")
    guarded = []
    baseline = []
    for seed in (canary_seed,) + paired_seeds:
        metric, receipt = one_game(seed, model, sha, engine, GUARD_LIMIT, 3000)
        if receipt is None:
            raise RuntimeError(f"Guarded real TavernGym game still did not finish seed={seed}")
        if seed == canary_seed:
            file = out_dir / f"001-{seed}.json"
        else:
            file = out_dir / f"paired-{seed}.json"
        file.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        guarded.append(metric)
        if seed in paired_seeds:
            b = baseline_game(seed, SESSION, "baseline")
            validate(b)
            baseline.append({"seed": seed, "rank": b["placements"][0],
                             "completed": b["completed"], "decisions": b["decisions"]})
    paired_candidate = [x for x in guarded if x["seed"] in paired_seeds]
    deltas = [a["rank"] - b["rank"] for a, b in zip(paired_candidate, baseline)]
    result = {
        "schema": 1, "session_id": SESSION, "source": "actual_taverngym",
        "engine": engine, "model_sha256": sha, "ppo_steps_in_this_audit": 0,
        "raw_probe": raw,
        "guarded_games": guarded,
        "baseline_paired_games": baseline,
        "paired_candidate_minus_baseline_rank_deltas": deltas,
        "paired_mean_rank_delta": statistics.mean(deltas),
        "all_guarded_games_completed": all(x["completed"] for x in guarded),
        "raw_game_strength_claim": False,
        "promotion": "none",
        "warning": "Guarded policy is assisted; do not interpret its rank as raw model strength. Raw probe may be incomplete.",
    }
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"raw": {"completed": raw["completed"],
                              "actions": raw["raw_model_actions"],
                              "action_categories": raw["action_category_counts"],
                              "legal_buy_opportunities": raw["legal_action_opportunities"].get("decisions_with_legal_buy", 0),
                              "same_observations": raw["observation_progress"].get("same_public_observation_as_previous", 0)},
                      "guarded_ranks": [r["rank"] for r in guarded],
                      "guard_forced_ends": [r["guard_forced_ends"] for r in guarded],
                      "paired_baseline_ranks": [b["rank"] for b in baseline],
                      "paired_delta": deltas, "promotion": "none"}), flush=True)
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    audit(args.model, args.out_dir, args.report)


if __name__ == "__main__":
    main()
