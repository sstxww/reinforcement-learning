"""Prespecified independent 20-seed, eight-seat-rotated replication of R001.

No tuning, fitting or parameter changes on these heldout seeds.
"""
from __future__ import annotations
import argparse, json, os, random, statistics
from datetime import datetime, timezone
from math import comb
from pathlib import Path
import numpy as np
from .baseline import BaselinePolicy
from .contract import ACTIONS, FEATURES, CARDS, verify_engine
from .sell_swap_1692601b import SellSwapPolicy, SID
from .validate_receipt import validate

HELDOUT = tuple(range(69131, 69151))
LOCKED_ARM = (7, "first")


def full_match_at_seat(seed: int, seat: int, candidate: bool) -> dict:
    import taverngym
    engine = verify_engine()
    if not 0 <= seat < 8:
        raise ValueError("Invalid controlled seat")
    if "Sell" not in taverngym.action_name(16) or "Buy" not in taverngym.action_name(8):
        raise RuntimeError("Unexpected TavernGym action encoding")
    game = taverngym.Game(seed=seed)
    if game.num_players != 8:
        raise RuntimeError("Not an eight-seat TavernGym environment")
    policy = SellSwapPolicy(*LOCKED_ARM) if candidate else BaselinePolicy()
    turn, used, decisions = -1, 0, 0
    for _ in range(30000):
        if game.is_over():
            break
        if int(game.turn) != turn:
            turn, used = int(game.turn), 0
        progress = False
        for p in range(8):
            if not game.needs_action(p):
                continue
            progress = True
            if p != seat:
                game.bot_play(p)
                continue
            fb, cb = game.observe2(seat)
            f = np.frombuffer(fb, dtype="<f4").copy()
            c = np.frombuffer(cb, dtype="<i4").copy()
            m = np.frombuffer(game.legal_mask(seat), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or m.shape != (ACTIONS,):
                raise RuntimeError("Incorrect observation at controlled seat")
            action = int(policy.act(
                {"features": f, "cards": c, "action_mask": m},
                {"turn": turn, "actions_used": used}))
            if not 0 <= action < ACTIONS or not m[action]:
                raise RuntimeError("Illegal policy action")
            game.step(seat, action)
            used += 1
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("No live progress")
    if not game.is_over():
        raise RuntimeError("Driver limit exceeded")
    places = [int(x) for x in game.placements()]
    result = dict(
        schema=1, timestamp=datetime.now(timezone.utc).isoformat(),
        environment="TavernGym", engine_version=engine["version"],
        engine_source_hash=engine["source_hash"], agent_id=SID,
        policy="sell_swap" if candidate else "baseline",
        policy_config=list(LOCKED_ARM) if candidate else None,
        controlled_seat=seat, controlled_placement=places[seat],
        seed=seed, completed=True, turns=int(game.turn), decisions=decisions,
        placements=places, truncated_combats=int(game.truncated_combats),
        turn_limit_end=bool(game.turn_limit_end), git_sha=os.getenv("GITHUB_SHA", ""),
        sales_interventions=policy.sales if candidate else 0,
        followup_buys=policy.buys if candidate else 0,
        unpaired_sales=policy.orphans if candidate else 0,
        safety_override_count=0, model_sha256=None)
    validate(result)
    return result


def summary(recs: list[dict]) -> dict:
    ranks = [r["controlled_placement"] for r in recs]
    return {"n": len(ranks), "ranks": ranks,
            "mean_rank": statistics.mean(ranks),
            "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
            "first_rate": sum(x == 1 for x in ranks) / len(ranks),
            "sales": sum(r["sales_interventions"] for r in recs),
            "unpaired_sales": sum(r["unpaired_sales"] for r in recs),
            "decisions": sum(r["decisions"] for r in recs)}


def paired_stats(differences: list[int]) -> dict:
    if not differences:
        raise ValueError("Empty evaluation")
    wins = sum(x < 0 for x in differences)
    losses = sum(x > 0 for x in differences)
    ties = sum(x == 0 for x in differences)
    n = wins + losses
    exact_sign_p = min(1.0, 2.0 * sum(comb(n, k) for k in range(min(wins, losses) + 1)) / 2 ** n) if n else 1.0
    rand = random.Random(1692601)
    means = sorted(statistics.mean(rand.choices(differences, k=len(differences))) for _ in range(10000))
    return {"candidate_minus_baseline": differences,
            "mean_rank_delta": statistics.mean(differences),
            "bootstrap95_percentile": [means[249], means[9749]],
            "wins": wins, "losses": losses, "ties": ties,
            "exact_two_sided_nonzero_sign_p": exact_sign_p,
            "interpretation": "Exploratory finite data; compare confidence interval with zero"}


def execute(out: Path, metrics: Path):
    out.mkdir(parents=True, exist_ok=True)
    metrics.parent.mkdir(parents=True, exist_ok=True)
    control, candidate = [], []
    for i, seed in enumerate(HELDOUT):
        seat = i % 8
        for is_candidate, group, suffix in [
            (False, control, "baseline"), (True, candidate, "candidate")]:
            rec = full_match_at_seat(seed, seat, is_candidate)
            (out / f"002-{suffix}-seed{seed}-seat{seat}.json").write_text(
                json.dumps(rec, indent=2, sort_keys=True), encoding="utf8")
            group.append(rec)
    diffs = [c["controlled_placement"] - b["controlled_placement"]
             for b, c in zip(control, candidate)]
    result = dict(schema=1, session_id=SID,
                  source_commit=os.getenv("GITHUB_SHA", ""),
                  engine_source_hash="6d8712c93022ba11",
                  inherited_R001="f0458b0bc357c83ee10306f798a2667cf91a6bca",
                  selection="prelocked turn >=7 first-slot sale, no new tuning",
                  neural_gradient_steps=0, heldout_games=40,
                  seeds=list(HELDOUT), seats=[i % 8 for i in range(len(HELDOUT))],
                  baseline=summary(control), candidate=summary(candidate),
                  pair=paired_stats(diffs),
                  warning="Seat-rotation is descriptive; no Arena, Champion, or 15000 MMR inference.")
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
