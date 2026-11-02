"""Isolated decision-budget ablation on genuine TavernGym eight-seat games.

The same simulation driver evaluates baseline and a 6-action-per-turn cap.
No fake/approximate engine and no model-training claims.
"""
from __future__ import annotations

import hashlib
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from tavern_ai.baseline import BaselinePolicy
from tavern_ai.contract import ACTIONS, CARDS, FEATURES, PATCH_SHA256, UPSTREAM_COMMIT, verify_engine
from tavern_ai.validate_receipt import validate

SESSION = "s-20261102-221336eb"
SEEDS = [73101, 73102, 73103, 73104, 73105, 73106]
CAP = 6
BASE_SHA = "315b068bac5ab6d8403c3c9b18f8c101c0cded5d"


class DecisionBudgetPolicy:
    """Finish the turn after CAP seat-0 decisions, but handle forced choices first."""

    def __init__(self, limit: int = CAP):
        if limit <= 0:
            raise ValueError("limit must be positive")
        self.limit = limit
        self.original = BaselinePolicy()
        self.interventions = 0

    def act(self, observation: dict, context: dict) -> int:
        mask = np.asarray(observation["action_mask"], dtype=bool)
        # Forced choice actions are never suppressed.
        if mask.shape == (ACTIONS,) and not mask[30:46].any():
            if context["actions_used"] >= self.limit and mask[0]:
                self.interventions += 1
                return 0
        return self.original.act(observation, context)


def game(seed: int, policy_name: str, source_hash: str) -> dict:
    import taverngym

    engine = verify_engine()
    instance = taverngym.Game(seed=seed)
    policy = BaselinePolicy() if policy_name == "baseline" else DecisionBudgetPolicy()
    decisions = 0
    illegal_actions = 0
    actions_this_turn = 0
    last_turn = -1
    for _ in range(30000):
        if instance.is_over():
            break
        turn = int(instance.turn)
        if turn != last_turn:
            last_turn, actions_this_turn = turn, 0
        progressed = False
        for seat in range(instance.num_players):
            if not instance.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                instance.bot_play(seat)
                continue
            fbytes, cbytes = instance.observe2(0)
            observation = {
                "features": np.frombuffer(fbytes, dtype="<f4").copy(),
                "cards": np.frombuffer(cbytes, dtype="<i4").copy(),
                "action_mask": np.frombuffer(
                    instance.legal_mask(0), dtype=np.uint8
                ).astype(bool),
            }
            if (observation["features"].shape != (FEATURES,)
                    or observation["cards"].shape != (CARDS,)
                    or observation["action_mask"].shape != (ACTIONS,)):
                raise ValueError("Unexpected pinned observe2 contract")
            mask = observation["action_mask"]
            if not mask.any():
                raise ValueError("No legal action")
            choice = int(policy.act(
                observation, {"turn": turn, "actions_used": actions_this_turn}
            ))
            if not 0 <= choice < ACTIONS or not mask[choice]:
                illegal_actions += 1
                raise ValueError("Illegal policy action")
            instance.step(0, choice)
            decisions += 1
            actions_this_turn += 1
        if not progressed and not instance.is_over():
            raise RuntimeError("Game stalled")
    if not instance.is_over():
        raise RuntimeError("Full-game safety limit exceeded")
    result = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym",
        "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION,
        "policy": policy_name,
        "seed": seed,
        "completed": bool(instance.is_over()),
        "turns": int(instance.turn),
        "decisions": decisions,
        "placements": [int(x) for x in instance.placements()],
        "truncated_combats": int(instance.truncated_combats),
        "turn_limit_end": bool(instance.turn_limit_end),
        "illegal_actions": illegal_actions,
        "budget_interventions": getattr(policy, "interventions", 0),
        "git_sha": os.getenv("GITHUB_SHA", ""),
        "policy_sha256": source_hash,
        "model_sha256": None,
    }
    validate(result)
    return result


def stats(results: list[dict]) -> dict:
    ranks = [row["placements"][0] for row in results]
    return {
        "games": len(ranks),
        "seeds": [row["seed"] for row in results],
        "placements": ranks,
        "mean_placement": statistics.mean(ranks),
        "first_place_rate": sum(x == 1 for x in ranks) / len(ranks),
        "top4_rate": sum(x <= 4 for x in ranks) / len(ranks),
        "mean_decisions": statistics.mean(row["decisions"] for row in results),
        "total_decisions": sum(row["decisions"] for row in results),
        "budget_interventions": sum(row["budget_interventions"] for row in results),
    }


def main() -> None:
    evidence_dir = Path("experiments") / SESSION
    research_dir = Path("research/sessions") / SESSION
    proposal_path = Path("research/knowledge/proposals") / f"{SESSION}-001.md"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    research_dir.mkdir(parents=True, exist_ok=True)
    proposal_path.parent.mkdir(parents=True, exist_ok=True)
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    baselines, candidates = [], []
    for seed in SEEDS:
        for policy, target in (
            ("baseline", baselines),
            (f"budget-{CAP}", candidates),
        ):
            row = game(seed, policy, source_hash)
            path = evidence_dir / (
                f"baseline-{seed}.json" if policy == "baseline" else f"001-{seed}.json"
            )
            path.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n")
            target.append(row)
            print(
                f"REAL_GAME seed={seed} policy={policy} "
                f"rank={row['placements'][0]} complete={row['completed']} "
                f"decisions={row['decisions']} "
                f"interventions={row['budget_interventions']}",
                flush=True,
            )
    b, c = stats(baselines), stats(candidates)
    differences = [
        x["placements"][0] - y["placements"][0]
        for x, y in zip(candidates, baselines, strict=True)
    ]
    run_url = (
        "https://github.com/sstxww/reinforcement-learning/actions/runs/"
        + os.getenv("GITHUB_RUN_ID", "not-in-actions")
    )
    report = {
        "session_id": SESSION,
        "baseline_commit": BASE_SHA,
        "running_commit": os.getenv("GITHUB_SHA", ""),
        "run_url": run_url,
        "upstream_commit": UPSTREAM_COMMIT,
        "patch_sha256": PATCH_SHA256,
        "engine_version": candidates[0]["engine_version"],
        "engine_source_hash": candidates[0]["engine_source_hash"],
        "policy_sha256": source_hash,
        "hypothesis": "Cap at six decisions per turn may save CPU decisions with little rank penalty",
        "max_decisions_per_turn": CAP,
        "baseline": b,
        "candidate": c,
        "paired_rank_differences_candidate_minus_baseline": differences,
        "paired_mean_rank_delta": statistics.mean(differences),
        "training_steps": 0,
        "candidate_is_best": False,
        "inference": "Exploratory 6 paired games; no superiority claim; independent confirmatory runs needed",
    }
    (research_dir / "evaluation.json").write_text(json.dumps(report, indent=2) + "\n")
    changed = c["budget_interventions"] > 0
    hypothesis_result = (
        "Candidate rank advantage not established; "
        + ("cap was exercised" if changed else "cap never intervened")
    )
    (research_dir / "round-001.md").write_text(
        f"""# Round 001 — seat-0 decision budget
Session: {SESSION}
Branch: agent/{SESSION}/optimization-001
Baseline main SHA: {BASE_SHA}
Experiment workflow: {run_url}
Executed commit: {os.getenv("GITHUB_SHA", "")}
Hypothesis: six non-forced seat-0 decisions/turn may reduce compute without rank loss.
Reason: branch-specific bounded policy evaluation avoids concurrent PPO and economy changes.
Learned from: main research/knowledge/INCIDENTS-20261102.md (full-game safety cap);
open reward/upgrade/receipt PRs were not taken as integrated results.
Changes: isolated experiment runner, per-turn wrapper, isolated one-shot Actions workflow, regression tests.
Environment: TavernGym {report["engine_version"]}; source {report["engine_source_hash"]};
upstream {UPSTREAM_COMMIT}; patch SHA256 {PATCH_SHA256}; observe2 4017/447, masked 245 actions.
Policy SHA256: {source_hash}; no neural model; no checkpoint.
Training steps: 0 (pure strategy ablation). Random seeds: {SEEDS}.
All {2*len(SEEDS)} games finished Game.is_over; each has 8 placements and real decisions.
Candidate placements: {c["placements"]}; mean {c["mean_placement"]}; first {c["first_place_rate"]}; top4 {c["top4_rate"]}.
Baseline placements: {b["placements"]}; mean {b["mean_placement"]}; first {b["first_place_rate"]}; top4 {b["top4_rate"]}.
Paired delta (lower is better): {report["paired_mean_rank_delta"]}; differences: {differences}.
Total seat-0 decisions: candidate {c["total_decisions"]}, baseline {b["total_decisions"]};
cap interventions {c["budget_interventions"]}.
Illegal actions 0; no combat truncation and no turn-limit endings (validated before save).
Evidence: experiments/{SESSION}/001-<seed>.json and baseline-<seed>.json;
metrics: research/sessions/{SESSION}/evaluation.json; run: {run_url}.
Failure/uncertainty: sample of six pairs, no superiority proven; {hypothesis_result}.
Model status: no candidate weight, Best unchanged; artifact retention 30 days only.
Next hypothesis: test alternative cap after independent sample expansion if interventions are material.
""", encoding="utf-8"
    )
    (research_dir / "STATUS.md").write_text(
        f"""# {SESSION} STATUS
- Round: 001, six paired seeds and 12 genuine TavernGym eight-seat games.
- Branch: agent/{SESSION}/optimization-001
- Base SHA: {BASE_SHA}; executed SHA: {os.getenv("GITHUB_SHA", "")}
- Workflow: {run_url}
- Result: {hypothesis_result}
- Candidate mean rank: {c["mean_placement"]}, baseline: {b["mean_placement"]}.
- Illegal moves: 0. Truncation/turn-limit: 0 (receipt validation).
- Model/checkpoint: none; strategy-only study; Best model not changed.
- Evidence: experiments/{SESSION}/, research/sessions/{SESSION}/evaluation.json
- PR: to be opened after job succeeds.
- Remaining: independent confirmation, owner review, no model promotion.
""", encoding="utf-8"
    )
    proposal_path.write_text(
        f"""# {SESSION} R001 — bounded baseline decision budget
This proposal is NOT merged/shared knowledge.
Hypothesis: cap non-forced seat-0 decisions at {CAP} per turn.
Six paired seeds {SEEDS}; same genuine TavernGym engine and opponent bots.
Candidate mean placement {c["mean_placement"]}; baseline {b["mean_placement"]};
paired candidate-minus-baseline delta {report["paired_mean_rank_delta"]}.
Candidate top4 {c["top4_rate"]}, first {c["first_place_rate"]};
baseline top4 {b["top4_rate"]}, first {b["first_place_rate"]}.
Total decisions candidate {c["total_decisions"]}, baseline {b["total_decisions"]};
cap interventions {c["budget_interventions"]}.
Verdict: {hypothesis_result}. No statistically established improvement, do not promote Best.
Training: none, policy-only; model and checkpoint are not applicable.
Reproduce via workflow {run_url}; code SHA256 {source_hash}.
Lessons: preserve mandatory choices; fail closed on mask; evaluate against paired seeds;
do not infer speed benefit from a cap that never intervenes.
Next: investigate action-count distribution / run confirmatory independent seeds.
""", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
