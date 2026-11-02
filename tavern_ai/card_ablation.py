"""Isolated and bounded card-embedding ablation; never alters shared trainer."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

from .contract import ACTIONS, CARDS, FEATURES, PATCH_SHA256, UPSTREAM_COMMIT, verify_engine

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def train_variant(dim: int, seed: int, steps: int, checkpoint_dir: Path) -> dict:
    from sb3_contrib import MaskablePPO
    from .env import TavernEnv
    from .model import TavernExtractor
    env = TavernEnv(seed=seed)
    try:
        obs, _ = env.reset(seed=seed)
        mask = env.action_masks()
        if obs["features"].shape != (FEATURES,) or obs["cards"].shape != (CARDS,):
            raise RuntimeError("Incompatible observation dimensions")
        if mask.shape != (ACTIONS,) or not mask.any() or mask.dtype != bool:
            raise RuntimeError("Missing/invalid legal-action mask")
        model = MaskablePPO(
            "MultiInputPolicy", env, device="cpu", verbose=0, seed=seed,
            n_steps=128, batch_size=64, n_epochs=4,
            gamma=0.99, gae_lambda=0.95, learning_rate=3e-4, ent_coef=0.01,
            policy_kwargs={
                "features_extractor_class": TavernExtractor,
                "features_extractor_kwargs": {
                    "features_dim": 256, "card_embedding_dim": dim
                },
                "net_arch": {"pi": [128], "vf": [128]}
            },
        )
        model.learn(total_timesteps=steps)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        path = checkpoint_dir / f"card-d{dim}.zip"
        model.save(str(path))
        model_meta = {
            "schema": 1, "variant": f"d{dim}", "seed": seed,
            "requested_timesteps": steps,
            "actual_timesteps": int(model.num_timesteps),
            "checkpoint_sha256": sha256(path),
            "embedding_dim": dim,
            "note": "Temporary GitHub Actions artifact; not persistent storage"
        }
        path.with_suffix(".metadata.json").write_text(
            json.dumps(model_meta, indent=2) + "\n", encoding="utf-8"
        )
        return {"checkpoint": str(path), **model_meta}
    finally:
        env.close()

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--agent-id", required=True)
    p.add_argument("--seed", type=int, default=27110)
    p.add_argument("--steps", type=int, default=128)
    p.add_argument("--start-seed", type=int, default=27111)
    p.add_argument("--games", type=int, default=2)
    args = p.parse_args()
    if not args.agent_id.startswith("s-") or "/" in args.agent_id:
        raise ValueError("Agent id must be a session ID")
    if not 128 <= args.steps <= 1024 or args.steps % 128:
        raise ValueError("Steps must be 128..1024 and divisible by 128")
    if not 1 <= args.games <= 3:
        raise ValueError("Bound evaluation to 1..3 games per variant")
    engine = verify_engine()
    from .canary import run as play_game
    base = Path("research/sessions") / args.agent_id
    receipts = Path("experiments") / args.agent_id
    checkpoints = Path("checkpoints") / args.agent_id
    base.mkdir(parents=True, exist_ok=True)
    receipts.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": 1, "session_id": args.agent_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "github_sha": os.getenv("GITHUB_SHA"),
        "github_run_url": f"https://github.com/sstxww/reinforcement-learning/actions/runs/{os.getenv('GITHUB_RUN_ID', 'unknown')}",
        "engine": engine, "upstream_commit": UPSTREAM_COMMIT,
        "patch_sha256": PATCH_SHA256,
        "train_seed": args.seed, "requested_timesteps_per_variant": args.steps,
        "eval_seeds": list(range(args.start_seed, args.start_seed + args.games)),
        "variants": {}
    }
    for dim in (8, 16):
        detail = train_variant(dim, args.seed, args.steps, checkpoints)
        ranks, failed = [], []
        detail["games"] = []
        for seed in report["eval_seeds"]:
            try:
                result = play_game(seed, args.agent_id, "model", detail["checkpoint"])
                receipt_path = receipts / f"001-{seed}-d{dim}.json"
                receipt_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
                rank = result["placements"][0]
                ranks.append(rank)
                detail["games"].append({
                    "seed": seed, "receipt": str(receipt_path),
                    "rank": rank, "decisions": result["decisions"],
                    "placements": result["placements"],
                    "truncated_combats": result["truncated_combats"],
                    "turn_limit_end": result["turn_limit_end"],
                })
            except Exception as exc:
                failed.append({"seed": seed, "error": repr(exc)})
        detail["failures"] = failed
        detail["completed_games"] = len(ranks)
        detail["mean_rank"] = statistics.mean(ranks) if ranks else None
        detail["top4_rate"] = sum(rank <= 4 for rank in ranks) / len(ranks) if ranks else None
        detail["first_place_rate"] = sum(rank == 1 for rank in ranks) / len(ranks) if ranks else None
        report["variants"][f"d{dim}"] = detail
        print(json.dumps({"variant": f"d{dim}", "actual_timesteps": detail["actual_timesteps"],
                          "mean_rank": detail["mean_rank"], "completed_games": len(ranks),
                          "failures": failed}, ensure_ascii=False), flush=True)
    report["total_actual_timesteps"] = sum(
        item["actual_timesteps"] for item in report["variants"].values()
    )
    report_path = base / "metrics-001.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    a, b = report["variants"]["d8"], report["variants"]["d16"]
    def fmt(detail: dict) -> str:
        if detail["completed_games"] == 0:
            return "unavailable (0 complete games)"
        return f"{detail['mean_rank']:.3f}; top4={detail['top4_rate']:.3f}; first={detail['first_place_rate']:.3f}; n={detail['completed_games']}"
    evidence = f"""# Round 001 · card embedding width ablation

- Session: `{args.agent_id}`
- Main base commit: `6ac59235b8238196a0e6462de77b72413c829372`
- Branch: `agent/{args.agent_id}/optimization-001`
- GitHub Actions run: {report['github_run_url']}
- Hypothesis: increasing the card embedding from 8 to 16 changes early MaskablePPO results without invalid actions.
- Prior reviewed material: `research/knowledge/README.md` has no confirmed card-width findings; open PR #6 baseline, #7 evaluation, #8 infrastructure, #9 trainer are unmerged leads, not verified improvements.
- Code: optional `card_embedding_dim` in `tavern_ai/model.py`; isolated `tavern_ai/card_ablation.py`; independent push workflow. Shared train.yml unchanged.
- Engine: {engine['version']}, source hash `{engine['source_hash']}`, upstream `{UPSTREAM_COMMIT}`, patch SHA256 `{PATCH_SHA256}`.
- Contract: {FEATURES} float features, {CARDS} card IDs, {ACTIONS} mask actions; shape and nonempty legal mask checked before training.
- Config: same seed={args.seed}, steps={args.steps} per variant; PPO n_steps=128, batch_size=64, epochs=4, gamma=.99, lambda=.95, LR=3e-4, entropy=.01; CPU, timeout from workflow.
- Actual training: d8={a['actual_timesteps']}, d16={b['actual_timesteps']}; total={report['total_actual_timesteps']}.
- Test seeds (paired): {report['eval_seeds']}.
- d8 mean rank / rates: {fmt(a)}
- d16 mean rank / rates: {fmt(b)}
- Incomplete game failures: d8={json.dumps(a['failures'])}; d16={json.dumps(b['failures'])}.
- Independent baseline receipt: `experiments/{args.agent_id}/001-27100.json` (created by separate genuine TavernGym canary workflow step).
- Model-game receipts: `experiments/{args.agent_id}/001-<seed>-d8.json`, `...-d16.json` only when an actual full match completes.
- Checkpoints: `checkpoints/{args.agent_id}/card-d8.zip` SHA256={a['checkpoint_sha256']}; `card-d16.zip` SHA256={b['checkpoint_sha256']}. Uploaded only to run-specific, expiring GitHub Actions artifact, **not permanently archived**.
- Verdict: tiny sample, performance improvement **unverified**; numerical rank differences are not statistically decisive. No TavernArena game or Elo.
- What worked: isolated CPU training and receipt recording, if supported by successful run and receipts.
- What did not work: any per-seed failures above. Otherwise no failure demonstrated; lack of power prevents positive claim.
- Clean-up: no weights, rollout, caches or virtual environments committed; retain run artifact while valid.
- Next: >=20 paired seeds, confidence intervals, investigate normalization/padding semantics separately before wider changes.
- PR: pending reviewer; never merge automatically.
"""
    (base / "round-001.md").write_text(evidence, encoding="utf-8")
    status = f"""# Session status

- Session ID: `{args.agent_id}`; round: 001
- Branch: `agent/{args.agent_id}/optimization-001`
- Code base: `6ac59235b8238196a0e6462de77b72413c829372`
- PR: pending (inspect branch PR after action completes)
- Training steps actually completed: {report['total_actual_timesteps']}
- Best verified score: not established; d8={fmt(a)}, d16={fmt(b)}; only scripted bots.
- Model checkpoints: run artifact at {report['github_run_url']}, under `checkpoints/{args.agent_id}/`; SHA256s in `metrics-001.json`.
- Recovery: download Actions artifact before expiry, verify SHA256, install pinned engine/patch, use saved model via `python -m tavern_ai.canary --agent-id {args.agent_id} --policy model --model checkpoints/{args.agent_id}/card-d16.zip --seed 27111 --receipt ...`. Artifact expiration means no permanent recovery.
- Next: run larger paired-seed comparison, then evaluate CPU time/memory trade-off.
"""
    (base / "STATUS.md").write_text(status, encoding="utf-8")
    proposal = f"""# {args.agent_id} · Round 001 evidence proposal

Unmerged preliminary evidence, **not a validated general improvement**.

- Hypothesis: double card embedding width 8 → 16 while preserving the original PPO trainer defaults.
- TavernGym: {engine['version']} / {engine['source_hash']}; upstream `{UPSTREAM_COMMIT}`.
- Training: d8={a['actual_timesteps']}, d16={b['actual_timesteps']} actual steps, equal seed {args.seed}.
- Paired seeds: {report['eval_seeds']}; d8={fmt(a)}; d16={fmt(b)}.
- Effective: optional width parameter works if tests and Action complete; no improvement established.
- Ineffective: no evidence either variant is competitive; see failures in session metrics.
- Why uncertain: short training and very small sample, scripted opponents; sample does not justify superiority.
- Evidence: {report['github_run_url']}, `research/sessions/{args.agent_id}/metrics-001.json`, complete match receipts in `experiments/{args.agent_id}/`.
- Recommendation: independent >=20 matched-seed matches, then include variance, runtime and memory before accepting width=16 in main.
"""
    Path("research/knowledge/proposals").mkdir(parents=True,exist_ok=True)
    (Path("research/knowledge/proposals") / f"{args.agent_id}-001.md").write_text(proposal, encoding="utf-8")
    print(json.dumps({"report": str(report_path), "actual_steps": report["total_actual_timesteps"],
                      "github_run": report["github_run_url"]}), flush=True)

if __name__ == "__main__":
    main()
