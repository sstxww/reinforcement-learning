"""Bounded sell/replace policy optimization on real TavernGym games.

Deployment inputs are only legal mask, own turn and action budget, never
hidden opponent information, RNG, future shop or simulator state.
"""
from __future__ import annotations
import argparse, json, os, statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SID = "s-20261102-1692601b"
TRAIN = (49131, 49132)
HELDOUT = (59131, 59132, 59133, 59134)
ARMS = ((7, "first"), (7, "last"), (11, "first"), (11, "last"))


class SellSwapPolicy:
    def __init__(self, min_turn: int, slot: str):
        if min_turn < 1 or slot not in ("first", "last"):
            raise ValueError("Bad parameters")
        self.min_turn, self.slot = min_turn, slot
        self.base = BaselinePolicy()
        self.turn, self.did_sell, self.pending = -1, False, False
        self.sales = self.buys = self.orphans = 0

    def act(self, obs: dict, context: dict) -> int:
        mask = np.asarray(obs["action_mask"], dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise ValueError("Invalid action mask")
        turn, used = int(context["turn"]), int(context["actions_used"])
        if self.turn != turn:
            if self.pending:
                self.orphans += 1
            self.turn, self.did_sell, self.pending = turn, False, False
        if mask[30:46].any():
            return self.base.act(obs, context)
        if self.pending:
            self.pending = False
            buy = np.flatnonzero(mask[8:16])
            if len(buy):
                self.buys += 1
                return 8 + int(buy[0])
            self.orphans += 1
        if (turn >= self.min_turn and used < 50 and not self.did_sell
                and mask[8:16].any() and mask[16:23].sum() == 7
                and not mask[46:196].any()):
            action = 16 if self.slot == "first" else 22
            if mask[action]:
                self.did_sell, self.pending = True, True
                self.sales += 1
                return action
        return self.base.act(obs, context)


def match(seed: int, arm: tuple | None) -> dict:
    import taverngym
    engine = verify_engine()
    if "Sell" not in taverngym.action_name(16) or "Buy" not in taverngym.action_name(8):
        raise RuntimeError("Pinned sell/buy actions changed")
    game = taverngym.Game(seed=seed)
    policy = SellSwapPolicy(*arm) if arm else BaselinePolicy()
    turn, used, decisions, hist = -1, 0, 0, Counter()
    for _ in range(30000):
        if game.is_over():
            break
        if int(game.turn) != turn:
            turn, used = int(game.turn), 0
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat:
                game.bot_play(seat)
                continue
            fb, cb = game.observe2(0)
            f = np.frombuffer(fb, dtype="<f4").copy()
            c = np.frombuffer(cb, dtype="<i4").copy()
            m = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or m.shape != (ACTIONS,):
                raise RuntimeError("Invalid observe2 contract")
            a = int(policy.act({"features": f, "cards": c, "action_mask": m},
                               {"turn": turn, "actions_used": used}))
            if not 0 <= a < ACTIONS or not m[a]:
                raise RuntimeError("Illegal selected action: " + str(a))
            game.step(0, a)
            hist["sell" if 16 <= a < 23 else
                 "buy" if 8 <= a < 16 else
                 "play_magnetize" if 46 <= a < 196 else
                 "upgrade" if a == 3 else
                 "end_turn" if a == 0 else "other"] += 1
            used += 1
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Game exceeded 30000-step driver limit")
    r = dict(schema=1, timestamp=datetime.now(timezone.utc).isoformat(),
             environment="TavernGym", engine_version=engine["version"],
             engine_source_hash=engine["source_hash"], agent_id=SID,
             policy="sell_swap" if arm else "baseline",
             policy_config=list(arm) if arm else None, seed=seed,
             completed=True, turns=int(game.turn), decisions=decisions,
             placements=[int(x) for x in game.placements()],
             truncated_combats=int(game.truncated_combats),
             turn_limit_end=bool(game.turn_limit_end), git_sha=os.getenv("GITHUB_SHA", ""),
             sales_interventions=policy.sales if arm else 0,
             followup_buys=policy.buys if arm else 0,
             unpaired_sales=policy.orphans if arm else 0,
             safety_override_count=0, action_histogram=dict(hist), model_sha256=None)
    validate(r)
    return r


def summarize(records):
    p = [r["placements"][0] for r in records]
    return dict(games=len(p), ranks=p, mean_rank=statistics.mean(p),
                top4_rate=sum(x <= 4 for x in p) / len(p),
                first_rate=sum(x == 1 for x in p) / len(p),
                sales=sum(x["sales_interventions"] for x in records),
                unpaired_sales=sum(x["unpaired_sales"] for x in records),
                decisions=sum(x["decisions"] for x in records))


def execute(out: Path, metrics: Path):
    out.mkdir(parents=True, exist_ok=True)
    metrics.parent.mkdir(parents=True, exist_ok=True)
    def game(phase, name, seed, arm):
        r = match(seed, arm)
        (out / ("001-" + phase + "-" + name + "-" + str(seed) + ".json")).write_text(
            json.dumps(r, indent=2, sort_keys=True), encoding="utf8")
        return r

    train_base = [game("train", "base", s, None) for s in TRAIN]
    train_arms = {}
    for arm in ARMS:
        name = "turn" + str(arm[0]) + "-" + arm[1]
        train_arms[name] = {"arm": list(arm), "result":
                            summarize([game("train", name, s, arm) for s in TRAIN])}
    eligible = [(v["result"]["mean_rank"], k) for k, v in train_arms.items()
                if v["result"]["sales"] > 0]
    selected = min(eligible)[1] if eligible else None
    chosen = tuple(train_arms[selected]["arm"]) if selected else None
    baseline = [game("heldout", "base", s, None) for s in HELDOUT]
    candidate = [game("heldout", "candidate", s, chosen) for s in HELDOUT] if chosen else []
    delta = [c["placements"][0] - b["placements"][0]
             for b, c in zip(baseline, candidate)]
    result = dict(session_id=SID, source_commit=os.getenv("GITHUB_SHA", ""),
                  engine_source_hash="6d8712c93022ba11",
                  training_method="finite real-game selection of 4 sale-swap parameter arms",
                  neural_gradient_steps=0, training_games=10,
                  train_seeds=list(TRAIN), train_baseline=summarize(train_base),
                  arms=train_arms, selected=selected,
                  heldout_seeds=list(HELDOUT),
                  heldout_baseline=summarize(baseline),
                  heldout_candidate=summarize(candidate) if candidate else None,
                  paired_rank_delta_candidate_minus_baseline=delta,
                  mean_delta=statistics.mean(delta) if delta else None,
                  conclusion="Exploratory; four heldout seeds cannot establish rank gain")
    metrics.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf8")
    print(json.dumps(result, ensure_ascii=False))
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--metrics", type=Path, required=True)
    a = p.parse_args()
    execute(a.out_dir, a.metrics)


if __name__ == "__main__":
    main()
