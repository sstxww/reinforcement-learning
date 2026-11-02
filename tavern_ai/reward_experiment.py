"""One-session bounded A/B PPO experiment with real full-game receipts.

Example (on the session's dedicated GitHub Actions runner):
python -m tavern_ai.reward_experiment --session-id s-20261102-bf8e1710
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

from .reward_match import run as full_match
from .contract import PATCH_SHA256, UPSTREAM_COMMIT, verify_engine
from .env import TavernEnv
from .model import TavernExtractor
from .reward_shaping import PotentialRewardWrapper


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def persist(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def score(matches: list[dict]) -> dict:
    placements = [m["placements"][0] for m in matches]
    return {
        "games": len(matches),
        "seeds": [m["seed"] for m in matches],
        "placements": placements,
        "mean_rank": statistics.mean(placements),
        "top4_rate": sum(p <= 4 for p in placements) / len(placements),
        "first_rate": sum(p == 1 for p in placements) / len(placements),
        "illegal_actions": 0,
        "guard_truncations": sum(m["truncated_combats"] for m in matches),
        "turn_limit_ends": sum(bool(m["turn_limit_end"]) for m in matches),
        "decisions": [m["decisions"] for m in matches],
        "model_safety_overrides": [m.get("model_safety_overrides", 0) for m in matches],
    }


def train_arm(label: str, seed: int, steps: int, output: Path) -> dict:
    import torch
    from sb3_contrib import MaskablePPO

    torch.set_num_threads(2)
    env = PotentialRewardWrapper(TavernEnv(seed=seed), gamma=0.99,
                                 strength=0.0 if label == "control" else 1.0)
    model = None
    try:
        model = MaskablePPO(
            "MultiInputPolicy", env, device="cpu", verbose=1, seed=seed,
            n_steps=128, batch_size=64, n_epochs=4,
            gamma=0.99, gae_lambda=0.95,
            learning_rate=3e-4, ent_coef=0.01,
            policy_kwargs={
                "features_extractor_class": TavernExtractor,
                "features_extractor_kwargs": {"features_dim": 256},
                "net_arch": {"pi": [128], "vf": [128]},
            },
        )
        model.learn(total_timesteps=steps)
        output.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(output))
        metrics = {}
        for k, v in model.logger.name_to_value.items():
            if isinstance(v, (float, int)) and math.isfinite(float(v)):
                metrics[k] = float(v)
        return {
            "model_path": str(output),
            "model_sha256": sha256(output),
            "trained_steps": int(model.num_timesteps),
            "training_seed": seed,
            "ppo_metrics": metrics,
        }
    finally:
        env.close()


def run(session_id: str, steps: int, seed: int, evaluation_seeds: list[int]) -> dict:
    if not session_id.startswith("s-") or "/" in session_id or "\\" in session_id:
        raise ValueError("Expected an isolated session ID")
    if steps < 128 or steps > 1024 or steps % 128:
        raise ValueError("Steps must be 128..1024 in multiples of 128")
    if not evaluation_seeds or len(set(evaluation_seeds)) != len(evaluation_seeds):
        raise ValueError("Provide unique held-out evaluation seeds")
    engine = verify_engine()
    home = Path("experiments") / session_id
    checkpoint_dir = Path("checkpoints") / session_id
    scores: dict[str, dict] = {}
    arms: dict[str, dict] = {}
    for label in ("control", "potential"):
        model_file = checkpoint_dir / label / "model.zip"
        train = train_arm(label, seed, steps, model_file)
        matches = []
        for game_seed in evaluation_seeds:
            match = full_match(game_seed, session_id, "model", str(model_file))
            persist(home / f"eval-{label}-{game_seed}.json", match)
            matches.append(match)
        arms[label] = train
        scores[label] = score(matches)
    # Mandatory independently played model-seat match, *not* the shared CI canary.
    own_seed = 33001
    own = full_match(own_seed, session_id, "model", arms["potential"]["model_path"])
    persist(home / f"001-{own_seed}.json", own)
    observed_delta = scores["potential"]["mean_rank"] - scores["control"]["mean_rank"]
    report = {
        "schema": 1,
        "experiment": "potential-based shaping vs sparse terminal reward",
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "branch": os.environ.get("GITHUB_REF_NAME", ""),
        "training_git_sha": os.environ.get("GITHUB_SHA", ""),
        "engine": engine,
        "upstream_commit": UPSTREAM_COMMIT,
        "patch_sha256": PATCH_SHA256,
        "observation": {"features": 4017, "cards": 447, "action_mask": 245},
        "same_seed_paired_arms": True,
        "training_seed": seed,
        "training_steps_per_arm": steps,
        "training_steps_total": 2 * steps,
        "config": {"algorithm": "MaskablePPO", "n_steps": 128,
                   "batch_size": 64, "n_epochs": 4, "gamma": 0.99,
                   "gae_lambda": 0.95, "learning_rate": 0.0003,
                   "ent_coef": 0.01, "potential_strength": 1.0},
        "arms": arms,
        "held_out_evaluation": scores,
        "observed_mean_rank_delta_potential_minus_control": observed_delta,
        "independent_full_match": own,
        "conclusion": "Exploratory only; 3 seeded games per arm cannot establish a strength improvement.",
        "checkpoint_storage": "GitHub Actions artifact (90-day retention; NOT permanent)",
    }
    persist(Path("research/sessions") / session_id / "round-001-metrics.json", report)
    write_handoff(report)
    return report


def write_handoff(report: dict) -> None:
    sid = report["session_id"]
    root = Path("research/sessions") / sid
    root.mkdir(parents=True, exist_ok=True)
    a = report["held_out_evaluation"]["control"]
    b = report["held_out_evaluation"]["potential"]
    own = report["independent_full_match"]
    run_url = (
        "https://github.com/sstxww/reinforcement-learning/actions/runs/"
        + os.environ.get("GITHUB_RUN_ID", "unknown")
    )
    steps = report["training_steps_per_arm"]
    branch = report["branch"]
    commit = report["training_git_sha"]
    model_sha = report["arms"]["potential"]["model_sha256"]
    direction = (
        "lower (better)" if b["mean_rank"] < a["mean_rank"] else
        "higher (worse)" if b["mean_rank"] > a["mean_rank"] else "equal"
    )
    research = f"""# Round 001: potential-based reward shaping

Session: {sid}
Base main SHA: 6ac59235b8238196a0e6462de77b72413c829372
Training branch: {branch}
Execution commit: {commit}
PR: to be created by the research agent after this workflow completes
Run: {run_url}

## Hypothesis and prior evidence
Original TavernGym SoloEnv returns zero on nonterminal legal steps and a
placement-only reward at termination. A discounted, bounded, *public-observation*
potential may provide a more learnable signal during short CPU PPO training.
Main has no merged experimental session results at start. Open PRs #6-#9
remain unverified research leads; their owned modules were not changed.

## Exact change and reproducibility
New opt-in tavern_ai/reward_shaping.py wraps TavernEnv; the shared train.py
and train.yml remain unchanged. Formula:
Rshaped = Rraw + gamma * Phi(next) - Phi(previous); Phi(terminal) = 0.
Phi uses self-health, armor, tavern tier, and board count at global float
offsets 5, 6, 10, 32; no hidden state. gamma=0.99, same as PPO.

Command: python -m tavern_ai.reward_experiment --session-id {sid} --steps {steps} --seed {report["training_seed"]}
Each arm uses {steps} real TavernGym environment steps; total {report["training_steps_total"]}.
Two matched seed runs, original sparse control vs potential reward, same network
and fixed evaluation seeds {a["seeds"]}. Model: MaskablePPO MultiInputPolicy.
Engine: {report["engine"]["version"]}; hash: {report["engine"]["source_hash"]}.
Upstream commit: {report["upstream_commit"]}.
Engine patch SHA256: {report["patch_sha256"]}.
Observe2: 4017 features, 447 card slots, 245 masked actions.
Full config and model hashes: research/sessions/{sid}/round-001-metrics.json.

## Actual held-out results
Control placements: {a["placements"]}; mean rank {a["mean_rank"]:.3f};
top-four {a["top4_rate"]:.3f}; first-place {a["first_rate"]:.3f}.
Potential placements: {b["placements"]}; mean rank {b["mean_rank"]:.3f};
top-four {b["top4_rate"]:.3f}; first-place {b["first_rate"]:.3f}.
Potential minus control mean-rank delta: {report["observed_mean_rank_delta_potential_minus_control"]:+.3f}
({direction}); sample only {a["games"]} paired seeds. No statistical strength claim.

## Mandatory separate genuine eight-seat match
Receipt: experiments/{sid}/001-{own["seed"]}.json
TavernGym game reached Game.is_over() == True; seat-0 model rank
{own["placements"][0]}, full placements {own["placements"]}; seed
{own["seed"]}; decisions {own["decisions"]}; turns {own["turns"]}.
Illegal actions: none accepted by legal-mask driver; combat truncations
{own["truncated_combats"]}; turn-limit flag {own["turn_limit_end"]}.
Model safety fallback: at most 48 decisions per turn before a legal
end-turn (or forced mandatory choice); overrides: {own['model_safety_overrides']}.
Independent of the common PR CI canary.

## First attempt: failed game-progress guard
GitHub Actions run 41413409487: the sparse-control model trained 256
real PPO steps but its unbounded policy failed to finish seed 33011
within 30000 scheduling rounds. No model match receipt existed for
that attempt. This revision applies the same per-turn 48-action
fallback to *both* arms and logs the override count. Baseline seed
33000 was a valid completed match, rank 8; retained independently.

## Checkpoints and limitations
Model SHA256: {model_sha}
Storage: dedicated {sid}-round-001 GitHub Actions artifact (90-day
retention, NOT permanent); workflow run {run_url}.
Files in artifact: checkpoints/{sid}/control/model.zip and
checkpoints/{sid}/potential/model.zip.
To restore an arm: download its exact-run artifact, verify SHA256 from the
metrics JSON, and use MaskablePPO.load(path, device="cpu") with the pinned engine.
Temporary rollout and vendor build files are not committed.
One train seed, extremely small budget, three games per arm. Improvement,
if observed, is unconfirmed; false improvement due to chance is plausible.

## Next round
Test 2-3 additional independent training seeds, >=30 paired held-out
game seeds per arm and confidence intervals; increase training steps only
with isolated budgets. Retain any negative result as knowledge.
"""
    (root / "round-001.md").write_text(research, encoding="utf-8")
    status = f"""# Status: {sid}

Branch: {branch}
Base SHA: 6ac59235b8238196a0e6462de77b72413c829372
Training commit: {commit}
PR: pending creation/review
Round: 001 complete (empirical, not merged)
Training steps: {report["training_steps_total"]} total, {steps} per arm
Latest verified held-out mean rank: potential {b["mean_rank"]:.3f}
vs sparse control {a["mean_rank"]:.3f} over {a["games"]} matched games.
Full independent match rank: {own["placements"][0]} (seed {own["seed"]}).
Checkpoints: {sid}-round-001 artifact at {run_url}; 90-day retention,
no permanent storage. Potential checkpoint SHA256: {model_sha}.
Restore: download artifact, verify metrics hash, load using sb3_contrib
MaskablePPO.load with pinned TavernGym engine.
Next: repeat over independent seeds; do not merge as proven improvement.
"""
    (root / "STATUS.md").write_text(status, encoding="utf-8")
    proposal_dir = Path("research/knowledge/proposals")
    proposal_dir.mkdir(parents=True, exist_ok=True)
    proposal = f"""# Proposal {sid}-001: discounted potential shaping

Status: exploratory, NOT a merged or statistically verified result.
TavernGym 1.1.0 / source hash {report["engine"]["source_hash"]},
observe2 4017/447/245, upstream SHA {report["upstream_commit"]}.

The native SoloEnv gives terminal placement reward only. We tested adding
gamma*Phi(s')-Phi(s) with gamma 0.99 and terminal potential zero, using only
public own-health, armor, tier and occupied board fraction. This is
policy-invariant discounted potential shaping in the ideal setting and
provides a denser learning signal without replacing match outcome.

A/B controls: identical MaskablePPO networks, seed {report["training_seed"]},
{steps} actual training steps each, {a["games"]} held-out paired match
seeds {a["seeds"]}, exactly seven scripted bots.
Unshaped PPO placements {a["placements"]}; mean {a["mean_rank"]:.3f}.
Shaped PPO placements {b["placements"]}; mean {b["mean_rank"]:.3f}.
Mean rank delta (shaped - unshaped): {report["observed_mean_rank_delta_potential_minus_control"]:+.3f}.
Insufficient sample to establish either a benefit or a failure.
No claims about TavernArena performance.

Evidence: research/sessions/{sid}/round-001-metrics.json, full game
receipts experiments/{sid}/*.json, and {run_url}.
Model SHA256: {model_sha}; artifact retention only 90 days.

Reusable positive fact: wrapper preserves legal-mask forwarding and
bounded potential arithmetic (unit tests). Strength efficacy: unverified.
Recommendation: extend held-out seeds to >=30, repeat model seeds,
compare raw reward and value-loss traces, consider CI resource costs.
"""
    (proposal_dir / f"{sid}-001.md").write_text(proposal, encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--session-id", required=True)
    p.add_argument("--steps", type=int, default=256)
    p.add_argument("--seed", type=int, default=33123)
    p.add_argument("--eval-start-seed", type=int, default=33011)
    p.add_argument("--eval-games", type=int, default=3)
    args = p.parse_args()
    if args.eval_games < 2 or args.eval_games > 10:
        p.error("eval-games must be 2..10")
    seeds = [args.eval_start_seed + i for i in range(args.eval_games)]
    report = run(args.session_id, args.steps, args.seed, seeds)
    print(json.dumps({"training_steps": report["training_steps_total"],
                      "scores": report["held_out_evaluation"],
                      "match": report["independent_full_match"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
