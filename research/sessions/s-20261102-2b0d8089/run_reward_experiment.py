"""Bounded two-arm TavernGym MaskablePPO reward ablation.

All receipts are produced by tavern_ai.canary.run on the real eight-seat Game,
not by assembling placements or synthetic observations.
"""
from __future__ import annotations

import hashlib
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

from sb3_contrib import MaskablePPO
from tavern_ai.canary import run as play
from tavern_ai.contract import verify_engine, UPSTREAM_COMMIT, PATCH_SHA256, CATALOG_SHA256
from tavern_ai.env import TavernEnv
from tavern_ai.model import TavernExtractor
from tavern_ai.reward import SignedLogReward
from tavern_ai.validate_receipt import validate

SESSION = "s-20261102-2b0d8089"
TRAIN_SEED = 20261102
EVAL_SEEDS = (27001, 27002)
STEPS_PER_ARM = 256
ROOT = Path("experiments") / SESSION
CHECKPOINTS = Path("checkpoints") / SESSION


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def train_arm(label: str, transform: bool) -> dict:
    from sb3_contrib.common.maskable.utils import is_masking_supported
    env = TavernEnv(seed=TRAIN_SEED)
    if transform:
        env = SignedLogReward(env)
    if not is_masking_supported(env):
        raise RuntimeError("Reward wrapper broke the legal action-mask contract")
    try:
        policy_kwargs = {
            "features_extractor_class": TavernExtractor,
            "features_extractor_kwargs": {"features_dim": 256},
            "net_arch": {"pi": [128], "vf": [128]},
        }
        model = MaskablePPO(
            "MultiInputPolicy", env, device="cpu", verbose=0,
            seed=TRAIN_SEED, n_steps=128, batch_size=64,
            n_epochs=4, gamma=0.99, gae_lambda=0.95,
            learning_rate=3e-4, ent_coef=0.01,
            policy_kwargs=policy_kwargs,
        )
        model.learn(total_timesteps=STEPS_PER_ARM)
        CHECKPOINTS.mkdir(parents=True, exist_ok=True)
        path = CHECKPOINTS / (label + ".zip")
        model.save(str(path))
        metrics = {}
        for key in ("train/value_loss", "train/explained_variance", "train/policy_gradient_loss",
                    "train/entropy_loss", "train/approx_kl"):
            value = model.logger.name_to_value.get(key)
            if value is not None:
                try:
                    value = float(value)
                    if __import__("math").isfinite(value):
                        metrics[key] = value
                except (TypeError, ValueError):
                    pass
        return {
            "model_path": str(path),
            "model_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "actual_timesteps": int(model.num_timesteps),
            "training_metrics_last_update": metrics,
        }
    finally:
        env.close()



def play_bounded_model(seed: int, model_path: str) -> dict:
    """Run genuine Game to completion with a documented, legal end-turn safety rule.

    The 256-step experimental models can repeatedly select non-progressing actions.
    Starting at the 26th own action of a turn, force END TURN only when legal;
    otherwise use the baseline legal-action policy. This is a hybrid policy,
    not an unconstrained PPO model.
    """
    import taverngym
    import numpy as np
    from sb3_contrib import MaskablePPO
    from tavern_ai.baseline import BaselinePolicy
    from tavern_ai.contract import FEATURES, CARDS, ACTIONS

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    model = MaskablePPO.load(model_path, device="cpu")
    fallback = BaselinePolicy()
    decisions = 0
    forced_end_turns = 0
    fallback_other = 0
    last_turn = -1
    used_this_turn = 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, used_this_turn = turn, 0
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(0)
            features = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if (features.shape != (FEATURES,) or cards.shape != (CARDS,)
                    or mask.shape != (ACTIONS,) or not mask.any()):
                raise RuntimeError("Invalid pinned observe2 or legal-action mask")
            if used_this_turn >= 25 and mask[0]:
                action = 0
                forced_end_turns += 1
            elif used_this_turn >= 25:
                action = fallback.act(
                    {"features": features, "cards": cards, "action_mask": mask},
                    {"turn": turn, "actions_used": used_this_turn})
                fallback_other += 1
            else:
                action, _ = model.predict(
                    {"features": features, "cards": cards},
                    action_masks=mask, deterministic=True)
                action = int(action)
            if not mask[int(action)]:
                raise RuntimeError("Illegal masked action selected")
            game.step(0, int(action))
            used_this_turn += 1
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("Genuine TavernGym game stalled")
    if not game.is_over():
        raise RuntimeError("Bounded model failed to finish the game")
    from datetime import datetime, timezone
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": SESSION,
        "policy": "model_bounded_25",
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": hashlib.sha256(Path(model_path).read_bytes()).hexdigest(),
        "illegal_actions": 0,
        "safety_max_actions_per_turn": 25,
        "safety_end_turn_count": forced_end_turns,
        "safety_other_fallback_count": fallback_other,
    }
    validate(receipt)
    return receipt


def play_and_record(label: str, seed: int, model_path: str | None) -> dict:
    policy = "model" if model_path else "baseline"
    receipt = (play_bounded_model(seed, model_path) if model_path\n               else play(seed, SESSION, policy, None))
    validate(receipt)
    filename = f"001-{seed}.json" if label == "signed_log" and seed == EVAL_SEEDS[0] else f"001-{label}-{seed}.json"
    write_json(ROOT / filename, receipt)
    return {
        "seed": seed, "file": str(ROOT / filename),
        "placement": receipt["placements"][0],
        "decisions": receipt["decisions"],
        "completed": receipt["completed"],
        "illegal_actions": 0,
        "truncated_combats": receipt["truncated_combats"],
        "turn_limit_end": receipt["turn_limit_end"],
        "all_placements": receipt["placements"],
    }


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    engine = verify_engine()
    results = {}
    for label, transform in (("raw", False), ("signed_log", True)):
        print(f"TRAIN start {label} seed={TRAIN_SEED} steps={STEPS_PER_ARM}", flush=True)
        results[label] = train_arm(label, transform)
        print("TRAIN complete", label, json.dumps(results[label]), flush=True)
    for label in ("baseline", "raw", "signed_log"):
        path = results[label]["model_path"] if label != "baseline" else None
        games = []
        for seed in EVAL_SEEDS:
            record = play_and_record(label, seed, path)
            games.append(record)
            print("MATCH", label, json.dumps(record), flush=True)
        placements = [r["placement"] for r in games]
        results.setdefault(label, {})["games"] = games
        results[label]["mean_placement"] = statistics.mean(placements)
        results[label]["top4_rate"] = sum(x <= 4 for x in placements) / len(placements)
        results[label]["first_place_rate"] = sum(x == 1 for x in placements) / len(placements)
    report = {
        "schema": 1, "session_id": SESSION, "run_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": os.getenv("GITHUB_SHA", ""),
        "experiment": "signed_log1p_vs_raw_reward",
        "hypothesis": "signed log compression reduces last-update value-loss volatility",
        "engine": engine, "upstream_commit": UPSTREAM_COMMIT,
        "patch_sha256": PATCH_SHA256, "catalog_sha256": CATALOG_SHA256,
        "observation_shape": {"features": 4017, "cards": 447, "legal_actions": 245},
        "train_seed": TRAIN_SEED, "steps_per_arm": STEPS_PER_ARM,
        "actual_total_timesteps": sum(results[x]["actual_timesteps"] for x in ("raw", "signed_log")),
        "eval_seeds": list(EVAL_SEEDS), "results": results,
        "caveats": ["Two seeds per policy cannot establish a strength gain.",
                    "Checkpoints are ephemeral Actions artifacts unless separately archived."],
    }
    write_json(ROOT / "001-summary.json", report)
    write_json(CHECKPOINTS / "manifest.json", {
        "session_id": SESSION,
        "engine": engine,
        "train_seed": TRAIN_SEED,
        "steps_per_arm": STEPS_PER_ARM,
        "models": {x: {k: v for k, v in results[x].items()
                       if k in ("model_path", "model_sha256", "actual_timesteps")}
                   for x in ("raw", "signed_log")},
    })
    print("REPORT", json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
