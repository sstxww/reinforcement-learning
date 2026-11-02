"""R002: real-game official-bot teacher vs V0 teacher, old BC and new BC.

Isolated empirical teacher-quality comparison with same BC architecture and
same 80 supervised updates; never uses hidden state as learner input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

import torch

from .bc_session_661adf61 import (
    MaskedBC, SESSION_ID, TRAIN_SEEDS, distill, observe, play,
    receipt, summarize, teacher_accuracy, MAX_GAME_STEPS,
)
from .contract import verify_engine
from .validate_receipt import validate

EVAL_SEEDS = tuple(range(66901, 66911))
EXPECTED_OLD_HASH = "b77aab475a502dacd2c036f4df87cbadd4656299bf5baaa13f16569b04699cd8"


def play_official_bot(seed: int, collect: bool = False):
    """Seat 0 uses the engine bot_action; all student data are public observe2."""
    import taverngym

    game = taverngym.Game(seed=int(seed))
    samples = []
    decisions = 0
    for _ in range(MAX_GAME_STEPS):
        if game.is_over():
            break
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat == 0:
                features, cards, mask = observe(game, 0)
                action = int(game.bot_action(0))
                if not mask[action]:
                    raise RuntimeError("Official bot action violates public legal mask")
                if collect:
                    samples.append((features, cards, mask, action))
                game.step(0, action)
                decisions += 1
            else:
                game.bot_play(seat)
        if not progressed and not game.is_over():
            raise RuntimeError("Game stalled with no seat ready")
    if not game.is_over():
        return {"completed": False, "policy": "official_bot", "seed": int(seed),
                "reason": "full_game_limit", "decisions": decisions}, samples
    return receipt(game, seed, "official_bot", decisions), samples


def histogram(samples):
    categories = {
        "end_turn": range(0, 1), "refresh": range(1, 2),
        "freeze": range(2, 3), "upgrade": range(3, 4),
        "hero_power": range(4, 8), "buy": range(8, 16),
        "sell": range(16, 23), "activate": range(23, 30),
        "choose": range(30, 46), "play": range(46, 126),
        "magnetize": range(126, 196), "move": range(196, 245),
    }
    action_counts = Counter(int(s[3]) for s in samples)
    return {k: sum(v for action, v in action_counts.items() if action in ids)
            for k, ids in categories.items()}


def load_old_model(path: Path, card_count: int):
    old_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if old_hash != EXPECTED_OLD_HASH:
        raise ValueError("Old candidate SHA256 mismatch")
    saved = torch.load(path, map_location="cpu", weights_only=True)
    if saved["engine"] != verify_engine() or saved["card_count"] != card_count:
        raise ValueError("Old BC checkpoint engine mismatch")
    old = MaskedBC(card_count)
    old.load_state_dict(saved["state_dict"])
    old.eval()
    return old, old_hash


def paired_stats(primary, other):
    by_a = {r["seed"]: r for r in primary if r.get("completed")}
    by_b = {r["seed"]: r for r in other if r.get("completed")}
    common = sorted(set(by_a) & set(by_b))
    deltas = [by_a[s]["placements"][0] - by_b[s]["placements"][0] for s in common]
    return {"paired_completed": len(common), "paired_seeds": common,
            "per_seed_rank_delta": deltas,
            "mean_rank_delta": sum(deltas) / len(deltas) if deltas else None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--old-model", type=Path, required=True)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    engine = verify_engine()
    old, old_hash = load_old_model(args.old_model, int(engine["n_cards"]))
    train_samples = []
    train_matches = []
    for seed in TRAIN_SEEDS:
        rec, samples = play_official_bot(seed, collect=True)
        if not rec.get("completed"):
            raise RuntimeError("Official teacher failed full game")
        train_matches.append(rec)
        train_samples.extend(samples)
    student, metrics = distill(train_samples, int(engine["n_cards"]), updates=80)
    model_path = args.outdir / "official-bc-model.pt"
    torch.save({"state_dict": student.state_dict(), "card_count": int(engine["n_cards"]),
                "engine": engine, "training_seeds": TRAIN_SEEDS,
                "updates": 80, "teacher": "taverngym.Game.bot_action(0)"}, model_path)
    new_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    eval_records = {"official_bot": [], "v0_baseline": [], "old_bc_raw": [], "official_bc_raw": []}
    accuracy = []
    for seed in EVAL_SEEDS:
        official, obs = play_official_bot(seed, collect=True)
        eval_records["official_bot"].append(official)
        accuracy.append(teacher_accuracy(student, obs))
        base, _ = play(seed, "teacher")
        eval_records["v0_baseline"].append(base)
        old_rec, _ = play(seed, "bc_raw", model=old)
        old_rec["policy"] = "old_bc_raw"
        eval_records["old_bc_raw"].append(old_rec)
        new_rec, _ = play(seed, "bc_raw", model=student)
        new_rec["policy"] = "official_bc_raw"
        eval_records["official_bc_raw"].append(new_rec)
    report = {
        "schema": 2, "session": SESSION_ID, "round": 2,
        "main_base": "315b068bac5ab6d8403c3c9b18f8c101c0cded5d",
        "engine": engine,
        "training_seeds": list(TRAIN_SEEDS), "heldout_seeds": list(EVAL_SEEDS),
        "teacher_train_receipts": train_matches,
        "official_teacher_action_histogram": histogram(train_samples),
        "train": metrics, "actual_ppo_timesteps": 0,
        "old_model_sha256": old_hash, "new_model_sha256": new_hash,
        "heldout_teacher_accuracy": accuracy,
        "matches": eval_records,
        "summary": {k: summarize(v) for k, v in eval_records.items()},
        "paired_new_vs_old_bc": paired_stats(eval_records["official_bc_raw"], eval_records["old_bc_raw"]),
        "paired_new_vs_official_teacher": paired_stats(eval_records["official_bc_raw"], eval_records["official_bot"]),
        "paired_new_vs_v0": paired_stats(eval_records["official_bc_raw"], eval_records["v0_baseline"]),
        "interpretation": "Descriptive 10-seed teacher-source comparison; teacher state visitation and sample counts are not controlled. No formal promotion.",
    }
    for match in train_matches:
        validate(match)
    for match_list in eval_records.values():
        for match in match_list:
            if match.get("completed"):
                validate(match)
    (args.outdir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("RESULT_JSON=" + json.dumps(report, ensure_ascii=False, separators=(",", ":")))
    print("NEW_MODEL_SHA256=" + new_hash)


if __name__ == "__main__":
    main()
