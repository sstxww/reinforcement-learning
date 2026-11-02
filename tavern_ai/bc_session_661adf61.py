"""Isolated masked behavior-cloning pilot, NOT a promoted game agent.

Collects real eight-seat TavernGym teacher decisions, trains a small policy,
then tests raw and explicitly end-turn-guarded inference on unseen seeds.
No hidden state, future shop, opponent hand, or engine RNG is used as model input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from torch import nn

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION_ID = "s-20261102-661adf61"
TRAIN_SEEDS = (65101, 65102, 65103)
EVAL_SEEDS = (65901, 65902)
MAX_GAME_STEPS = 30000
RAW_TURN_LIMIT = 130
GUARD_TURN_LIMIT = 85


def observe(game, seat=0):
    """Use exactly the public observation and legal mask provided to the seat."""
    fbytes, cbytes = game.observe2(seat)
    features = np.frombuffer(fbytes, dtype="<f4").copy()
    cards = np.frombuffer(cbytes, dtype="<i4").copy()
    mask = np.frombuffer(game.legal_mask(seat), dtype=np.uint8).astype(bool)
    if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
        raise ValueError("Pinned observe2 dimensions changed")
    if not np.isfinite(features).all() or not mask.any():
        raise ValueError("Invalid observable features or empty legal-action mask")
    return features, cards, mask


class MaskedBC(nn.Module):
    """Small teacher-distillation model, separate from the PPO baseline."""

    def __init__(self, card_count: int):
        super().__init__()
        self.card_embedding = nn.Embedding(card_count, 8, padding_idx=0)
        self.numeric = nn.Sequential(nn.Linear(FEATURES, 96), nn.Tanh())
        self.card_net = nn.Sequential(nn.Linear(CARDS * 8, 96), nn.Tanh())
        self.actor = nn.Sequential(nn.Linear(192, 128), nn.Tanh(), nn.Linear(128, ACTIONS))

    def forward(self, features, cards, mask):
        x = torch.clamp(features.float(), -100.0, 100.0) / 10.0
        y = self.card_embedding(cards.long()).flatten(1)
        logits = self.actor(torch.cat((self.numeric(x), self.card_net(y)), dim=1))
        return logits.masked_fill(~mask.bool(), -1e9)


def choose_legal(model, features, cards, mask):
    model.eval()
    with torch.no_grad():
        logits = model(
            torch.from_numpy(features).unsqueeze(0),
            torch.from_numpy(cards.astype(np.int64)).unsqueeze(0),
            torch.from_numpy(mask).unsqueeze(0),
        )
        action = int(torch.argmax(logits, dim=1).item())
    if not mask[action]:
        raise RuntimeError("Model emitted illegal action")
    return action


def receipt(game, seed, policy, decisions, guards=0):
    engine = verify_engine()
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION_ID,
        "policy": policy,
        "seed": int(seed),
        "completed": True,
        "turns": int(game.turn),
        "decisions": int(decisions),
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "forced_end_turns": int(guards),
        "git_sha": os.environ.get("GITHUB_SHA", ""),
    }
    validate(result)
    return result


def play(seed, policy, model=None, collect=False):
    """Control only seat 0; seven other seats use TavernGym bot_play."""
    import taverngym

    game = taverngym.Game(seed=int(seed))
    teacher = BaselinePolicy()
    samples = []
    decisions = 0
    guard_count = 0
    actions_this_turn = 0
    last_turn = None
    for _ in range(MAX_GAME_STEPS):
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
            features, cards, mask = observe(game, seat)
            if policy == "teacher":
                action = teacher.act(
                    {"features": features, "cards": cards, "action_mask": mask},
                    {"turn": turn, "actions_used": actions_this_turn},
                )
            elif policy in {"bc_raw", "bc_guarded"} and model is not None:
                if policy == "bc_raw" and actions_this_turn >= RAW_TURN_LIMIT:
                    return {
                        "completed": False, "policy": policy, "seed": int(seed),
                        "reason": "raw_turn_budget_exceeded",
                        "turn": turn, "actions_this_turn": actions_this_turn,
                        "decisions": decisions,
                    }, samples
                if policy == "bc_guarded" and actions_this_turn >= GUARD_TURN_LIMIT and mask[0]:
                    action = 0
                    guard_count += 1
                else:
                    action = choose_legal(model, features, cards, mask)
            else:
                raise ValueError("Unknown policy or missing model")
            if not mask[action]:
                raise RuntimeError("Teacher/model violated legal mask")
            if collect:
                samples.append((features, cards, mask, int(action)))
            game.step(0, int(action))
            decisions += 1
            actions_this_turn += 1
        if not progressed and not game.is_over():
            raise RuntimeError("TavernGym stalled")
    if not game.is_over():
        return {
            "completed": False, "policy": policy, "seed": int(seed),
            "reason": "game_step_budget_exceeded", "decisions": decisions,
        }, samples
    return receipt(game, seed, policy, decisions, guard_count), samples


def stack(samples):
    if not samples:
        raise ValueError("Teacher collected no samples")
    features = torch.from_numpy(np.stack([s[0] for s in samples]))
    cards = torch.from_numpy(np.stack([s[1] for s in samples]).astype(np.int64))
    masks = torch.from_numpy(np.stack([s[2] for s in samples]))
    actions = torch.tensor([s[3] for s in samples], dtype=torch.long)
    if not bool(masks.gather(1, actions[:, None]).all()):
        raise ValueError("Teacher labels contain illegal actions")
    return features, cards, masks, actions


def distill(samples, card_count, seed=65100, updates=80, batch=64):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(2)
    data = stack(samples)
    model = MaskedBC(card_count)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    rng = np.random.default_rng(seed)
    losses = []
    model.train()
    for _ in range(updates):
        idx = torch.as_tensor(rng.integers(0, len(samples), size=min(batch, len(samples))), dtype=torch.long)
        logits = model(data[0][idx], data[1][idx], data[2][idx])
        loss = nn.functional.cross_entropy(logits, data[3][idx])
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.item()))
    return model, {"supervised_updates": updates, "teacher_states": len(samples),
                   "first_loss": losses[0], "last_loss": losses[-1],
                   "optimizer": "Adam", "batch_size": min(batch, len(samples))}


def teacher_accuracy(model, samples):
    if not samples:
        return None
    data = stack(samples)
    model.eval()
    correct = 0
    with torch.no_grad():
        for i in range(0, len(samples), 32):
            logits = model(data[0][i:i+32], data[1][i:i+32], data[2][i:i+32])
            correct += int((logits.argmax(1) == data[3][i:i+32]).sum().item())
    return {"matches": correct, "total": len(samples), "accuracy": correct / len(samples)}


def summarize(receipts):
    completed = [r for r in receipts if r.get("completed")]
    positions = [r["placements"][0] for r in completed]
    return {
        "attempted": len(receipts), "completed": len(completed),
        "placements": positions,
        "mean_placement": sum(positions) / len(positions) if positions else None,
        "top4_rate": sum(p <= 4 for p in positions) / len(positions) if positions else None,
        "first_place_rate": sum(p == 1 for p in positions) / len(positions) if positions else None,
        "forced_end_turns": sum(r.get("forced_end_turns", 0) for r in completed),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--updates", type=int, default=80)
    args = parser.parse_args()
    if not 1 <= args.updates <= 160:
        raise ValueError("Budget: supervised updates must be 1..160")
    engine = verify_engine()
    args.outdir.mkdir(parents=True, exist_ok=True)
    training_data = []
    train_matches = []
    for seed in TRAIN_SEEDS:
        match, samples = play(seed, "teacher", collect=True)
        if not match.get("completed"):
            raise RuntimeError("Teacher failed to finish the real game")
        train_matches.append(match)
        training_data.extend(samples)
    model, metrics = distill(training_data, int(engine["n_cards"]), updates=args.updates)
    checkpoint = args.outdir / "bc-model.pt"
    torch.save({"state_dict": model.state_dict(), "card_count": int(engine["n_cards"]),
                "engine": engine, "seed": 65100, "updates": args.updates}, checkpoint)
    model_sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    eval_records = {"teacher": [], "bc_raw": [], "bc_guarded": []}
    accuracies = []
    for seed in EVAL_SEEDS:
        teacher, heldout = play(seed, "teacher", collect=True)
        eval_records["teacher"].append(teacher)
        accuracies.append(teacher_accuracy(model, heldout))
        guarded, _ = play(seed, "bc_guarded", model=model)
        eval_records["bc_guarded"].append(guarded)
        if seed == EVAL_SEEDS[0]:
            raw, _ = play(seed, "bc_raw", model=model)
            eval_records["bc_raw"].append(raw)
    report = {
        "schema": 1, "session": SESSION_ID, "experiment": "masked_behavior_cloning",
        "training_seeds": list(TRAIN_SEEDS), "heldout_seeds": list(EVAL_SEEDS),
        "engine": engine, "model_sha256": model_sha,
        "actual_ppo_timesteps": 0, "train": metrics,
        "teacher_train_receipts": train_matches,
        "heldout_teacher_accuracy": accuracies,
        "matches": eval_records,
        "summary": {key: summarize(value) for key, value in eval_records.items()},
        "decision": "RETEST",
        "notes": "Raw and forced-end-turn models are strictly separate. No claim of competitive improvement.",
    }
    report_path = args.outdir / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("RESULT_JSON=" + json.dumps(report, ensure_ascii=False, separators=(",", ":")))
    print("CHECKPOINT_SHA256=" + model_sha)


if __name__ == "__main__":
    main()
