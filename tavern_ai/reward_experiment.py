"""Two-arm, finite PPO reward-shaping experiment with real full-game receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from pathlib import Path

from .canary import run as run_full_game
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .env import TavernEnv
from .potential_reward import GAMMA, PotentialRewardWrapper

SESSION_ID = "s-20261102-bedfc382"
EVAL_SEEDS = (31011, 31012, 31013)
TRAIN_SEED = 22042
SHAPING_ALPHA = 0.5


def train_arm(name: str, alpha: float, steps: int, seed: int, output: Path):
    import torch
    from sb3_contrib import MaskablePPO
    from .model import TavernExtractor

    torch.set_num_threads(2)
    underlying = TavernEnv(seed=seed, verify=True)
    env = PotentialRewardWrapper(underlying, alpha=alpha, gamma=GAMMA)
    model = None
    start = time.monotonic()
    try:
        obs, _ = env.reset(seed=seed)
        assert obs["features"].shape == (FEATURES,)
        assert obs["cards"].shape == (CARDS,)
        assert env.action_masks().shape == (ACTIONS,)
        model = MaskablePPO(
            "MultiInputPolicy", env, device="cpu", verbose=0, seed=seed,
            n_steps=128, batch_size=64, n_epochs=4,
            gamma=GAMMA, gae_lambda=0.95,
            learning_rate=3e-4, ent_coef=0.01,
            policy_kwargs={
                "features_extractor_class": TavernExtractor,
                "features_extractor_kwargs": {"features_dim": 256},
                "net_arch": {"pi": [128], "vf": [128]},
            },
        )
        model.learn(total_timesteps=steps, reset_num_timesteps=False)
        output.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(output))
        return {
            "name": name, "alpha": alpha,
            "timesteps": int(model.num_timesteps),
            "seed": seed, "elapsed_seconds": round(time.monotonic() - start, 3),
            "rollout_decisions": env.steps,
            "terminated_episodes": env.terminal_count,
            "raw_reward_sum": round(env.raw_reward_sum, 6),
            "shaping_bonus_sum": round(env.bonus_sum, 6),
            "checkpoint": str(output),
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        }
    finally:
        env.close()


def evaluate_arm(name: str, model_path: Path, seeds: tuple[int, ...],
                 receipt_dir: Path | None):
    records = []
    for seed in seeds:
        result = run_full_game(seed, SESSION_ID, "model", str(model_path))
        if receipt_dir is not None:
            receipt_dir.mkdir(parents=True, exist_ok=True)
            target = receipt_dir / f"001-{seed}.json"
            target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        records.append(result)
    ranks = [r["placements"][0] for r in records]
    return {
        "arm": name, "games": len(records),
        "seeds": list(seeds),
        "placements_for_seat_zero": ranks,
        "all_placements": [r["placements"] for r in records],
        "decisions": [r["decisions"] for r in records],
        "mean_placement": statistics.mean(ranks),
        "top4_rate": sum(rank <= 4 for rank in ranks) / len(ranks),
        "first_place_rate": sum(rank == 1 for rank in ranks) / len(ranks),
        "truncated_combats": sum(r["truncated_combats"] for r in records),
        "turn_limit_ends": sum(r["turn_limit_end"] for r in records),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=256)
    parser.add_argument("--train-seed", type=int, default=TRAIN_SEED)
    parser.add_argument("--out", type=Path, default=Path("outputs/reward"))
    args = parser.parse_args()
    if args.steps < 128 or args.steps > 2048 or args.steps % 128:
        parser.error("steps must be a multiple of 128 in [128, 2048]")
    engine = verify_engine()
    output = args.out
    output.mkdir(parents=True, exist_ok=True)
    training = {}
    for arm, alpha in (("control", 0.0), ("shaped", SHAPING_ALPHA)):
        training[arm] = train_arm(
            arm, alpha, args.steps, args.train_seed, output / f"{arm}.zip"
        )
    evaluations = {}
    for arm in ("control", "shaped"):
        evaluations[arm] = evaluate_arm(
            arm, output / f"{arm}.zip", EVAL_SEEDS,
            Path("experiments") / SESSION_ID if arm == "shaped" else None,
        )
    differences = [
        s - c for s, c in zip(
            evaluations["shaped"]["placements_for_seat_zero"],
            evaluations["control"]["placements_for_seat_zero"],
        )
    ]
    result = {
        "schema": 1, "session_id": SESSION_ID,
        "hypothesis": "Potential shaping improves short-horizon PPO placement",
        "engine": engine, "gamma": GAMMA,
        "shaping_alpha": SHAPING_ALPHA,
        "train_seed": args.train_seed,
        "steps_per_arm": args.steps,
        "training": training, "evaluation": evaluations,
        "paired_shaped_minus_control_rank": differences,
        "mean_rank_difference": statistics.mean(differences),
        "interpretation": "Exploratory N=3 paired seeded games; no significance claim.",
        "checkpoint_retention": "GitHub Actions artifact (temporary; not durable)",
    }
    target = Path("research/sessions") / SESSION_ID / "metrics-001.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
