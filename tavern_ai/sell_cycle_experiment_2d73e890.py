"""Real eight-seat TavernGym policy-tuning experiment.

The 12 tuning games select an integer heuristic, *not* a neural checkpoint;
the 16 heldout games remain untouched until that integer has been fixed.
"""
import json
import os
import statistics
from pathlib import Path
import numpy as np
from .contract import FEATURES, CARDS, ACTIONS, verify_engine
from .sell_cycle_2d73e890 import SellCyclePolicy
from .validate_receipt import validate

SID = "s-20261102-2d73e890"
TRAIN_SEEDS = tuple(range(68310, 68314))
HOLDOUT_SEEDS = tuple(range(68410, 68418))
RECEIPTS = Path("experiments") / SID
REPORTS = Path("reports") / SID

def full_game(seed: int, budget: int, engine: dict) -> dict:
    import taverngym
    game = taverngym.Game(seed=seed)
    agent = SellCyclePolicy(budget=budget)
    decisions = 0
    last_turn, used = -1, 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, used = turn, 0
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(0)
            f = np.frombuffer(fbytes, dtype="<f4")
            c = np.frombuffer(cbytes, dtype="<i4")
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise RuntimeError("Pinned engine observation contract violated")
            action = agent.act({"features": f, "cards": c, "action_mask": mask},
                               {"turn": turn, "actions_used": used})
            if not mask[action]:
                raise RuntimeError("Illegal policy action")
            game.step(0, action)
            decisions += 1
            used += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Full game exceeded 30000 outer ticks")
    r = {
        "schema": 1,
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": SID,
        "policy": "baseline" if budget == 0 else "sell-cycle-budget-" + str(budget),
        "seed": int(seed),
        "completed": True,
        "turns": int(game.turn),
        "decisions": int(decisions),
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": None,
        "tuning_budget": budget,
        "sale_actions": agent.total_sells,
        "forced_end_count": agent.forced_ends,
    }
    validate(r)
    return r

def summarize(records):
    places = [x["placements"][0] for x in records]
    return {
        "games": len(records), "placements": places,
        "mean_placement": statistics.mean(places),
        "top4_rate": sum(p <= 4 for p in places) / len(places),
        "first_rate": sum(p == 1 for p in places) / len(places),
        "mean_sale_actions": statistics.mean(r["sale_actions"] for r in records),
        "forced_end_count": sum(r["forced_end_count"] for r in records),
        "all_completed_without_engine_guard": all(r["completed"] for r in records),
    }

def main():
    engine = verify_engine()
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    # Only training seeds determine selected strategy.
    train = {b: [full_game(s, b, engine) for s in TRAIN_SEEDS] for b in (0, 1, 2)}
    chosen = min((1, 2), key=lambda b: (summarize(train[b])["mean_placement"], b))
    controls, candidates = [], []
    for seed in HOLDOUT_SEEDS:
        control = full_game(seed, 0, engine)
        candidate = full_game(seed, chosen, engine)
        controls.append(control)
        candidates.append(candidate)
        path = RECEIPTS / ("001-" + str(seed) + ".json")
        path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    deltas = [c["placements"][0] - b["placements"][0] for c, b in zip(candidates, controls)]
    result = {
        "schema": 1,
        "session_id": SID,
        "main_base_sha": "315b068bac5ab6d8403c3c9b18f8c101c0cded5d",
        "engine": engine,
        "mechanism": "buy 8..15, sell 16..22, play 46..125, magnetize 126..195",
        "training_method": "bounded full-game heuristic parameter search, not PPO",
        "actual_ppo_steps": 0,
        "train_seeds": list(TRAIN_SEEDS),
        "holdout_seeds": list(HOLDOUT_SEEDS),
        "train": {str(b): summarize(g) for b, g in train.items()},
        "budget_selected_on_training_only": chosen,
        "holdout_control": summarize(controls),
        "holdout_challenger": summarize(candidates),
        "paired_placement_deltas_negative_is_better": deltas,
        "paired_mean_delta": statistics.mean(deltas),
        "caution": "Eight heldout paired seeds vs seven scripted bots; not Arena MMR, not established superiority.",
    }
    (REPORTS / "001-summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
