"""Heldout, public-observation probe of actual TavernGym action prerequisites.

This is supervised mechanics diagnostics, NOT a deployable Battlegrounds policy.
Labels come from the real current legal mask, but the model sees only 4017
public float observations. It never consumes the mask as an input feature.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

SESSION_ID = "s-20261102-0ecd90f7"
BASE_SHA = "315b068bac5ab6d8403c3c9b18f8c101c0cded5d"
SOURCE = "MCG-NJU/AutoTavern@fb61201a557ddd36a411cf44aac51ce4d9b606ce:crates/taverngym/src/actions.rs"
# Half-open ranges verified against the actual upstream Action::encode constants.
GROUPS = {
    "refresh": (1, 2),
    "freeze": (2, 3),
    "upgrade": (3, 4),
    "buy": (8, 16),
    "sell": (16, 23),
    "choose": (30, 46),
    "play": (46, 126),
    "magnetize": (126, 196),
}
TRAIN_SEEDS = [87900, 87901, 87902]
TEST_SEEDS = [87910, 87911]


def availability(mask: np.ndarray) -> np.ndarray:
    mask = np.asarray(mask, dtype=bool)
    if mask.shape != (ACTIONS,):
        raise ValueError("Expected the pinned 245-action legal mask")
    return np.array([mask[lo:hi].any() for lo, hi in GROUPS.values()], dtype=np.float32)


def collect_real_match(seed: int, engine: dict, receipt_dir: Path):
    """One actual eight-seat Game; 0 is V0 baseline, 1..7 official bots."""
    import taverngym

    game = taverngym.Game(seed=seed)
    baseline = BaselinePolicy()
    features, labels = [], []
    decisions = 0
    last_turn, actions_this_turn = -1, 0
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
            f = np.frombuffer(fbytes, dtype="<f4").copy()
            c = np.frombuffer(cbytes, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise RuntimeError("Unexpected observe2 dimensions")
            if not np.isfinite(f).all():
                raise RuntimeError("Nonfinite public observation")
            # Labels are recorded only to supervised targets; mask is not put in X.
            features.append(f)
            labels.append(availability(mask))
            action = baseline.act(
                {"features": f, "cards": c, "action_mask": mask},
                {"turn": turn, "actions_used": actions_this_turn},
            )
            if not mask[action]:
                raise RuntimeError("Illegal baseline action")
            game.step(0, int(action))
            actions_this_turn += 1
            decisions += 1
        if not progress and not game.is_over():
            raise RuntimeError("Game stalled")
    if not game.is_over():
        raise RuntimeError("Full-game safety limit exceeded")
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"],
        "agent_id": SESSION_ID,
        "policy": "baseline",
        "seed": seed,
        "completed": True,
        "turns": int(game.turn),
        "decisions": decisions,
        "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "model_sha256": None,
        "research_role": "public_observation_probe_data_collection_only",
    }
    validate(receipt)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    path = receipt_dir / f"001-{seed}.json"
    path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return np.stack(features), np.stack(labels), receipt


def prepare(x_train: np.ndarray, x_eval: np.ndarray, width: int = 128):
    """Unsupervised feature selection: training observations only."""
    a = np.clip(np.asarray(x_train, dtype=np.float32), -10000, 10000)
    b = np.clip(np.asarray(x_eval, dtype=np.float32), -10000, 10000)
    variance = a.var(axis=0)
    columns = np.argsort(-variance, kind="stable")[:width]
    mu = a[:, columns].mean(axis=0)
    sd = np.maximum(a[:, columns].std(axis=0), 1e-3)
    return (
        np.clip((a[:, columns] - mu) / sd, -8, 8),
        np.clip((b[:, columns] - mu) / sd, -8, 8),
        columns, mu, sd,
    )


def sigmoid(z: np.ndarray):
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))


def fit_probe(x: np.ndarray, y: np.ndarray, iterations: int = 240):
    """Deterministic full-batch multi-label logistic gradient updates."""
    prior = np.clip(y.mean(axis=0), 0.02, 0.98)
    weights = np.zeros((x.shape[1], y.shape[1]), dtype=np.float32)
    bias = np.log(prior / (1 - prior)).astype(np.float32)
    for _ in range(iterations):
        predictions = sigmoid(x @ weights + bias)
        diff = predictions - y
        weights -= 0.12 * (x.T @ diff / len(x) + 0.002 * weights)
        bias -= 0.12 * diff.mean(axis=0)
    return weights, bias


def compare(y_true: np.ndarray, predicted: np.ndarray, constant: np.ndarray):
    rows = {}
    for i, name in enumerate(GROUPS):
        truth = y_true[:, i] > 0.5
        guess = predicted[:, i] >= 0.5
        tp = int(np.sum(truth & guess))
        fp = int(np.sum(~truth & guess))
        fn = int(np.sum(truth & ~guess))
        tn = int(np.sum(~truth & ~guess))
        rows[name] = {
            "n": int(len(truth)),
            "true_prevalence": float(truth.mean()),
            "train_prevalence": float(constant[i]),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "f1": float(2 * tp / (2 * tp + fp + fn)) if tp or fp or fn else None,
            "model_brier": float(np.mean((predicted[:, i] - y_true[:, i]) ** 2)),
            "train_prior_brier": float(np.mean((constant[i] - y_true[:, i]) ** 2)),
        }
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--receipt-dir", type=Path, default=Path(f"experiments/{SESSION_ID}"))
    p.add_argument("--report-dir", type=Path, default=Path(f"reports/{SESSION_ID}"))
    a = p.parse_args()
    engine = verify_engine()
    train, test = [], []
    for seed in TRAIN_SEEDS + TEST_SEEDS:
        x, y, receipt = collect_real_match(seed, engine, a.receipt_dir)
        (train if seed in TRAIN_SEEDS else test).append((x, y, receipt))
    xtr = np.concatenate([d[0] for d in train])
    ytr = np.concatenate([d[1] for d in train])
    xte = np.concatenate([d[0] for d in test])
    yte = np.concatenate([d[1] for d in test])
    ztr, zte, columns, mu, sd = prepare(xtr, xte)
    w, b = fit_probe(ztr, ytr)
    pred = sigmoid(zte @ w + b)
    prior = ytr.mean(axis=0)
    family = compare(yte, pred, prior)
    a.report_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = a.report_dir / "001-compact-mechanics-probe.npz"
    np.savez_compressed(checkpoint, columns=columns, mean=mu, std=sd,
                        weights=w, bias=b, groups=np.array(list(GROUPS)))
    # Test independent restoration of the EXACT checkpoint bytes.
    with np.load(checkpoint, allow_pickle=False) as saved:
        restored = sigmoid(
            np.clip((np.clip(xte, -10000, 10000)[:, saved["columns"]] -
                     saved["mean"]) / saved["std"], -8, 8) @
            saved["weights"] + saved["bias"])
    if not np.allclose(pred, restored, atol=1e-6):
        raise RuntimeError("Checkpoint restoration does not reproduce predictions")
    sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    receipts = [d[2] for d in train + test]
    rank = [r["placements"][0] for r in receipts]
    summary = {
        "session": SESSION_ID, "base_sha": BASE_SHA,
        "source_action_layout": SOURCE, "engine": engine,
        "method": "public-observation logistic multi-label legal-family probe",
        "label_source": "real legal_mask targets, NEVER an input feature",
        "train_seeds": TRAIN_SEEDS, "heldout_seeds": TEST_SEEDS,
        "train_states": int(len(xtr)), "heldout_states": int(len(xte)),
        "gradient_updates": 240, "ppo_steps": 0,
        "selected_public_feature_columns": int(len(columns)),
        "checkpoint_sha256": sha, "checkpoint_restored": True,
        "family": family, "game_policy": "baseline, no learned policy evaluated",
        "complete_real_games": len(receipts), "ranks": rank,
        "mean_rank": float(np.mean(rank)),
        "top4_rate": float(np.mean(np.array(rank) <= 4)),
        "first_place_rate": float(np.mean(np.array(rank) == 1)),
        "simulator_guards_triggered": sum(
            int(r["turn_limit_end"]) + int(r["truncated_combats"]) for r in receipts
        ),
        "conclusion": "Mechanics diagnostic only. No demonstrated competitive improvement.",
        "promotion": "REJECT as Champion; RETEST diagnostic on more heldout seeds",
    }
    (a.report_dir / "001-metrics.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    session = Path("research/sessions") / SESSION_ID
    session.mkdir(parents=True, exist_ok=True)
    avg_gain = float(np.mean([
        row["train_prior_brier"] - row["model_brier"]
        for row in family.values()
    ]))
    match_lines = "\n".join(
        f"- seed {r['seed']}: seat0 rank {r['placements'][0]}; "
        f"decisions {r['decisions']}; complete={r['completed']}; "
        f"truncation={r['truncated_combats']}; guard={r['turn_limit_end']}"
        for r in receipts
    )
    core = f"""# {SESSION_ID} Round 001 — public-only mechanics precondition probe

- Base main: {BASE_SHA}; branch agent/{SESSION_ID}/optimization-001.
- Hypothesis: real action availability can be partially predicted from current
  public observe2 float features without using the legal mask as input; this
  tests a *narrow* prerequisite, not card synergies or strategic strength.
- Evidence source: {SOURCE}
- TavernGym version {engine['version']}; source {engine['source_hash']};
  public float features {FEATURES}, cards {CARDS}, actions {ACTIONS}.
- Teacher for state collection: main BaselinePolicy, seven official bots.
- Training: {len(xtr)} actual public training observations, seeds {TRAIN_SEEDS};
  {len(xte)} heldout observations, seeds {TEST_SEEDS}, full-batch
  multi-label logistic learner, **240 actual gradient updates**, 0 PPO steps.
- Probe average Brier reduction vs training-prior constant classifier:
  {avg_gain:.6f} (positive is better). Per-family confusion metrics and
  heldout prevalence: reports/{SESSION_ID}/001-metrics.json.
- Checkpoint: reports/{SESSION_ID}/001-compact-mechanics-probe.npz;
  SHA256 {sha}; verified independently reloaded and reproduced predictions.
- Real full TavernGym eight-seat matches: {len(receipts)}. Every receipt
  created from Game.is_over(), not synthetic or truncated:
{match_lines}
- Average seat0 placement {np.mean(rank):.3f}, top4 {summary['top4_rate']:.3f},
  first {summary['first_place_rate']:.3f}. These are baseline collection games,
  **NOT the trained mechanics classifier controlling a game**.
- No paired competing learned policy exists; promotion = REJECT for competitive
  Champion. RETEST mechanics generalization with balanced, unseen states.
- Distinguish mask legality, supervised predicate ability, and true competitive
  strategy; no validated card effect/synergy, combat planning, or self-play.
- Next: acquire more varied turn/hero/shop states and evaluate per-family
  errors before integrating a mechanics auxiliary into a deployable policy.
- Reproduce: pip install -e '.[test]'; bash scripts/bootstrap_engine.sh;
  python -m tavern_ai.mechanics_probe_0ecd90f7
- Model is a tiny NPZ checkpoint committed with the evidence; do not treat
  it as a MaskablePPO or a permanent Champion.
"""
    (session / "round-001.md").write_text(core, encoding="utf-8")
    (session / "STATUS.md").write_text(
        f"# {SESSION_ID}\n\n"
        f"Branch agent/{SESSION_ID}/optimization-001; main base {BASE_SHA}.\n"
        f"Round 001 diagnostics complete, subject to PR final-head CI.\n"
        f"Training updates: 240 logistic; PPO: 0. Restored checkpoint SHA256 {sha}.\n"
        f"Full matches {len(receipts)}; all baseline data collection. No learned "
        f"competition policy, no Champion recommendation.\n"
        f"Resume via python -m tavern_ai.mechanics_probe_0ecd90f7; see round-001.md.\n",
        encoding="utf-8")
    proposals = Path("research/knowledge/proposals")
    proposals.mkdir(parents=True, exist_ok=True)
    (proposals / f"{SESSION_ID}-001.md").write_text(
        "# Draft learning: public-observation mechanics legality probe\n\n" +
        core + "\nDo not merge as proof of strategy strength. "
        "Independent PR review and broader heldout verification required.\n",
        encoding="utf-8")
    print(json.dumps({
        "session": SESSION_ID, "train_states": len(xtr),
        "heldout_states": len(xte), "games": len(receipts),
        "ranks": rank, "mean_brier_improvement": avg_gain,
        "checkpoint_sha256": sha
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
