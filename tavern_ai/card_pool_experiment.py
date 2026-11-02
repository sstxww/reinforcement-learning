"""Independent bounded card-pooling MaskablePPO A/B and real eight-seat matches."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from .card_pool import SlotPooledExtractor
from .contract import ACTIONS, CARDS, FEATURES, UPSTREAM_COMMIT, PATCH_SHA256, verify_engine
from .env import TavernEnv
from .model import TavernExtractor
from .validate_receipt import validate

AGENT_ID = "s-20261102-e4c71b9d"
ARCHITECTURES = {"control": TavernExtractor, "pooled": SlotPooledExtractor}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def train_one(label, steps, seed, engine, model_dir):
    from sb3_contrib import MaskablePPO
    env = TavernEnv(seed=seed)
    start = time.monotonic()
    try:
        model = MaskablePPO("MultiInputPolicy", env, device="cpu", verbose=0,
                           seed=seed, n_steps=128, batch_size=64, n_epochs=2,
                           gamma=0.99, gae_lambda=0.95, learning_rate=3e-4,
                           ent_coef=0.01, policy_kwargs={
                               "features_extractor_class": ARCHITECTURES[label],
                               "features_extractor_kwargs": {"features_dim": 256},
                               "net_arch": {"pi": [128], "vf": [128]},
                           })
        model.learn(total_timesteps=steps)
        model_dir.mkdir(parents=True, exist_ok=True)
        path = model_dir / (label + ".zip")
        model.save(str(path))
        summary = {"model": label, "seed": seed,
                   "steps_requested": steps, "steps_actual": int(model.num_timesteps),
                   "elapsed_seconds": round(time.monotonic() - start, 2),
                   "sha256": sha(path), "model_path": str(path),
                   "engine": engine, "upstream_commit": UPSTREAM_COMMIT,
                   "patch_sha256": PATCH_SHA256,
                   "n_steps": 128, "batch_size": 64, "n_epochs": 2,
                   "learning_rate": 3e-4}
        path.with_suffix(".metadata.json").write_text(json.dumps(summary, indent=2))
        print(json.dumps({"training": summary}), flush=True)
        return path, summary
    finally:
        env.close()

def play(seed, label, model_path, engine):
    import taverngym
    from sb3_contrib import MaskablePPO
    game = taverngym.Game(seed=seed)
    model = MaskablePPO.load(str(model_path), device="cpu")
    last_turn, actions_this_turn, decisions, forced_ends = -1, 0, 0, 0
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
            f, c = game.observe2(0)
            obs = {"features": np.frombuffer(f, dtype="<f4").copy(),
                   "cards": np.frombuffer(c, dtype="<i4").copy()}
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if obs["features"].shape != (FEATURES,) or obs["cards"].shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("Simulator observation or mask format changed")
            if not np.isfinite(obs["features"]).all() or not mask.any():
                raise ValueError("Invalid observation or empty mask")
            if actions_this_turn >= 65 and mask[0]:
                action = 0
                forced_ends += 1
            else:
                action, _ = model.predict(obs, action_masks=mask, deterministic=True)
                action = int(action)
            if action < 0 or action >= ACTIONS or not mask[action]:
                raise ValueError(f"Illegal action {action}")
            game.step(0, action)
            decisions += 1
            actions_this_turn += 1
        if not progressed and not game.is_over():
            raise RuntimeError("Stalled eight-player simulation")
    if not game.is_over():
        raise RuntimeError("Real eight-player match did not finish before safety loop limit")
    result = {"schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
              "environment": "TavernGym", "engine_version": engine["version"],
              "engine_source_hash": engine["source_hash"],
              "agent_id": AGENT_ID, "policy": "model-" + label + "-bounded",
              "seed": seed, "completed": True, "turns": int(game.turn),
              "decisions": decisions, "placements": [int(x) for x in game.placements()],
              "truncated_combats": int(game.truncated_combats),
              "turn_limit_end": bool(game.turn_limit_end),
              "illegal_actions": 0, "forced_end_turns": forced_ends,
              "action_budget_per_turn": 65, "model_sha256": sha(model_path),
              "git_sha": os.environ.get("GITHUB_SHA", "")}
    validate(result)
    return result

def summarize(recs):
    ranks = [r["placements"][0] for r in recs]
    return {"games": len(ranks), "seeds": [r["seed"] for r in recs],
            "ranks": ranks, "mean_rank": statistics.mean(ranks),
            "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
            "first_rate": sum(x == 1 for x in ranks) / len(ranks),
            "illegal_actions": sum(r["illegal_actions"] for r in recs),
            "forced_end_turns": sum(r["forced_end_turns"] for r in recs)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=128)
    p.add_argument("--seed", type=int, default=32000)
    p.add_argument("--games", type=int, default=2)
    a = p.parse_args()
    if not 128 <= a.steps <= 512 or a.steps % 128:
        raise ValueError("Training steps must be a multiple of 128 in 128..512")
    if not 1 <= a.games <= 4:
        raise ValueError("Evaluation games must be 1..4")
    engine = verify_engine()
    model_dir = Path("checkpoints") / AGENT_ID
    report_dir = Path("reports") / AGENT_ID
    receipt_dir = Path("experiments") / AGENT_ID
    report_dir.mkdir(parents=True, exist_ok=True)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    models, train_reports = {}, {}
    for label in ARCHITECTURES:
        models[label], train_reports[label] = train_one(
            label, a.steps, a.seed, engine, model_dir)
    records = {}
    for label in ARCHITECTURES:
        records[label] = []
        for seed in range(a.seed + 11, a.seed + 11 + a.games):
            result = play(seed, label, models[label], engine)
            records[label].append(result)
            dest = (receipt_dir / f"001-{seed}.json" if label == "pooled"
                    else report_dir / f"control-{seed}.json")
            dest.write_text(json.dumps(result, ensure_ascii=False, indent=2))
            print(json.dumps({"policy": label, "seed": seed,
                              "rank": result["placements"][0],
                              "decisions": result["decisions"]}), flush=True)
    control, pooled = summarize(records["control"]), summarize(records["pooled"])
    report = {"session": AGENT_ID, "engine": engine,
              "upstream_commit": UPSTREAM_COMMIT, "patch_sha256": PATCH_SHA256,
              "algorithm": "MaskablePPO", "training": train_reports,
              "control": control, "pooled": pooled,
              "mean_rank_delta": pooled["mean_rank"] - control["mean_rank"],
              "claim": "Exploratory only; two seeds cannot prove skill improvement"}
    dest = report_dir / "ablation-001.json"
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({"report": str(dest), "control": control,
                      "pooled": pooled}, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
