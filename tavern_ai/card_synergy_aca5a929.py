"""Public-only, card-aware shop purchase target ranking.

Black-box parameter optimization on complete TavernGym eight-seat games.
Strictly separate training and heldout seeds; no hidden state or RNG.
This does NOT train a neural PPO policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .canary import run as baseline_run
from .contract import CATALOG_SHA256, verify_engine
from .validate_receipt import validate

SESSION_ID = "s-20261102-aca5a929"
TRAIN_SEEDS = (79110, 79111)
TEST_SEEDS = (79220, 79221, 79222, 79223)
N_SHOP = 8
N_BOARD = 7
N_HAND = 10


@dataclass(frozen=True)
class Weights:
    stat: float = 1.0
    tier: float = 0.5
    race: float = 0.0
    pair: float = 0.0


def card_offsets(layout: dict[str, int]) -> tuple[int, int, int]:
    """Observe2 card stream: hero, powers, deity, pending, quests, secrets,
    then board, hand and tavern. See upstream obs.rs (pinned source).
    """
    board = 1 + layout["N_POWERS"] + 2 + 3 * layout["N_QUESTS"] + layout["N_SECRETS"]
    hand = board + layout["N_BOARD"]
    shop = hand + layout["N_HAND"]
    return board, hand, shop


@lru_cache(maxsize=1)
def catalog() -> tuple[np.ndarray, dict[str, int]]:
    import taverngym
    columns, raw = taverngym.card_static()
    array = np.frombuffer(raw, dtype="<f4").reshape(-1, int(columns))
    dims = dict(taverngym.layout())
    if columns < 26 or array.shape[0] != taverngym.N_CARDS:
        raise ValueError("Incompatible card metadata layout")
    if (dims["N_SHOP"], dims["N_BOARD"], dims["N_HAND"], dims["N_ACTIONS"]) != (8, 7, 10, 245):
        raise ValueError("Incompatible action dimensions")
    board, hand, shop = card_offsets(dims)
    if shop + N_SHOP > dims["OBS_CARDS"]:
        raise ValueError("Card stream offset out of bounds")
    return array, dims


def best_buy(observation: dict, weights: Weights, static: np.ndarray, dims: dict[str,int]) -> int | None:
    """Returns legal minion purchase action; None when no legal minion purchase.

    Features are own publicly visible board/hand/shop indices, never private state.
    Uses only catalog static metadata (kind, tier, attack, health, races).
    """
    cards = np.asarray(observation["cards"], dtype=np.int64)
    mask = np.asarray(observation["action_mask"], dtype=bool)
    board, hand, shop = card_offsets(dims)
    if cards.shape != (dims["OBS_CARDS"],) or mask.shape != (245,):
        raise ValueError("Incorrect observe2 input shape")
    owned = np.concatenate((cards[board:board + N_BOARD], cards[hand:hand + N_HAND]))
    owned = owned[(owned > 0) & (owned < len(static))]
    minion_owned = owned[static[owned, 0] > 0.5]
    race_counts = (static[minion_owned, 15:26] > 0.5).sum(axis=0) if len(minion_owned) else np.zeros(11)
    race_counts = np.minimum(race_counts, 4)
    best = None
    best_score = -float("inf")
    for i in range(N_SHOP):
        if not mask[8+i]:
            continue
        idx = int(cards[shop+i])
        if not 0 < idx < len(static) or static[idx, 0] <= 0.5:
            continue
        row = static[idx]
        pair_count = int(np.count_nonzero(minion_owned == idx))
        synergy = float(np.dot(row[15:26] > 0.5, race_counts))
        score = (weights.stat * (max(float(row[11]), 0.0) + max(float(row[12]), 0.0)) / 10
                 + weights.tier * float(row[10])
                 + weights.race * synergy
                 + weights.pair * min(2, pair_count))
        if score > best_score:
            best_score, best = score, 8+i
    return best


class CardAwarePolicy:
    def __init__(self, weights: Weights):
        self.weights = weights
        self.baseline = BaselinePolicy()
        self.static, self.dims = catalog()
        self.changed_buys = 0
        self.buy_opportunities = 0
        self.guard_ends = 0

    def act(self, observation: dict, context: dict) -> int:
        base = self.baseline.act(observation, context)
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if int(context.get("actions_used", 0)) >= 85 and base == 0:
            self.guard_ends += 1
        if not 8 <= base < 16:
            return base
        self.buy_opportunities += 1
        selected = best_buy(observation, self.weights, self.static, self.dims)
        if selected is None:
            return base
        if selected != base:
            self.changed_buys += 1
        assert mask[selected]
        return int(selected)


def play_game(seed: int, weights: Weights, label: str) -> dict:
    import taverngym
    engine = verify_engine()
    policy = CardAwarePolicy(weights)
    game = taverngym.Game(seed=seed)
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
            fbytes, cbytes = game.observe2(0)
            observation = {
                "features": np.frombuffer(fbytes, dtype="<f4").copy(),
                "cards": np.frombuffer(cbytes, dtype="<i4").copy(),
                "action_mask": np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool),
            }
            action = policy.act(observation, {"turn":turn, "actions_used":actions_this_turn})
            if not observation["action_mask"][action]:
                raise AssertionError(f"Illegal purchase decision {action} seed={seed}")
            game.step(0, int(action))
            decisions += 1
            actions_this_turn += 1
        if not progress and not game.is_over():
            raise RuntimeError(f"Game stalled seed={seed}")
    if not game.is_over():
        raise RuntimeError(f"Safety loop exhausted seed={seed}")
    result = {
        "schema":1, "timestamp":datetime.now(timezone.utc).isoformat(),
        "environment":"TavernGym", "engine_source_hash":engine["source_hash"],
        "engine_version":engine["version"], "catalog_sha256":CATALOG_SHA256,
        "agent_id":SESSION_ID, "policy":label, "seed":seed,
        "completed":True, "turns":int(game.turn),
        "decisions":decisions, "placements":[int(x) for x in game.placements()],
        "truncated_combats":int(game.truncated_combats),
        "turn_limit_end":bool(game.turn_limit_end),
        "guard_interventions":policy.guard_ends,
        "changed_buys":policy.changed_buys,
        "buy_opportunities":policy.buy_opportunities,
        "model_sha256":None, "git_sha":os.getenv("GITHUB_SHA", ""),
    }
    validate(result)
    return result


def save_json(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def summary(games: list[dict]) -> dict:
    places = [x["placements"][0] for x in games]
    return {
        "n":len(games), "seeds":[x["seed"] for x in games],
        "ranks":places, "mean_rank":statistics.mean(places),
        "top4_rate":sum(x <= 4 for x in places)/len(places),
        "first_rate":sum(x == 1 for x in places)/len(places),
        "completed":sum(bool(x["completed"]) for x in games),
        "guard_interventions":sum(x.get("guard_interventions",0) for x in games),
        "changed_buys":sum(x.get("changed_buys",0) for x in games),
    }


def experiment() -> dict:
    engine = verify_engine()
    _, dims = catalog()
    if tuple(card_offsets(dims)) != (19,26,36):
        raise RuntimeError("Unrecognized card layout")
    root = Path("experiments") / SESSION_ID
    report_root = Path("reports") / SESSION_ID
    # Finite black-box search; training games are part of the optimization, NOT heldout eval.
    grid = [
        Weights(race=0.0,pair=0.0),
        Weights(race=0.7,pair=0.0),
        Weights(race=1.8,pair=0.0),
        Weights(race=0.7,pair=3.5),
    ]
    trials = []
    for index, w in enumerate(grid):
        rows = []
        for seed in TRAIN_SEEDS:
            r = play_game(seed, w, f"card_aware_train_{index}")
            save_json(root / f"001-train-{index}-{seed}.json", r)
            rows.append(r)
        trials.append({"index":index, "weights":asdict(w), "performance":summary(rows)})
    # Frozen selection from training only: lower rank is better; deterministic first tie.
    winner = min(trials, key=lambda v:(v["performance"]["mean_rank"],v["index"]))
    selected = grid[winner["index"]]
    checkpoint = {
        "schema":1, "session":SESSION_ID, "algorithm":"finite-grid-black-box-policy-search",
        "source_commit":os.getenv("GITHUB_SHA",""),
        "engine":engine, "catalog_sha256":CATALOG_SHA256,
        "actual_training_games":len(grid)*len(TRAIN_SEEDS),
        "gradient_steps":0, "ppo_steps":0,
        "train_seeds":list(TRAIN_SEEDS), "heldout_seeds":list(TEST_SEEDS),
        "weights":asdict(selected),
    }
    cp_path = report_root / "001-weights.json"
    save_json(cp_path,checkpoint)
    digest = hashlib.sha256(cp_path.read_bytes()).hexdigest()
    # Separate independent-seed full eight-seat comparisons.
    controls, challenger = [], []
    for seed in TEST_SEEDS:
        b = baseline_run(seed,SESSION_ID,"baseline")
        save_json(root / f"001-baseline-{seed}.json",b)
        controls.append(b)
        c = play_game(seed,selected,"card_aware_heldout")
        c["model_sha256"] = digest
        save_json(root / f"001-card-aware-{seed}.json",c)
        challenger.append(c)
    diffs = [a["placements"][0]-b["placements"][0] for a,b in zip(challenger,controls)]
    report = {
        "session":SESSION_ID, "method":"4-grid black-box parameter search",
        "rules_version":engine, "catalog_sha256":CATALOG_SHA256,
        "train_trials":trials, "selected_index":winner["index"],
        "actual_training_games":len(grid)*len(TRAIN_SEEDS),
        "gradient_steps":0, "ppo_steps":0,
        "checkpoint":str(cp_path),"checkpoint_sha256":digest,
        "heldout_baseline":summary(controls),"heldout_challenger":summary(challenger),
        "paired_rank_deltas":diffs, "paired_mean_delta":statistics.mean(diffs),
        "inference":"Only four heldout paired seeds: descriptive, not evidence of superiority",
        "promote":False,
    }
    save_json(report_root/"001-results.json",report)
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",action="store_true")
    args=parser.parse_args()
    if not args.run:
        parser.error("Explicit --run required (bounded 8 train + 8 heldout games)")
    experiment()


if __name__=="__main__":
    main()
