"""Isolated, seed-paired play-position ablation on the real TavernGym engine.

Only the position used for a legal Play action changes. This intentionally
does not edit the shared baseline, canary, or PPO code.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import canary
from .baseline import BaselinePolicy
from .contract import ENGINE_HASH, PATCH_SHA256, UPSTREAM_COMMIT
from .validate_receipt import validate

VERSION = "rightmost-play-v1"
PLAY_START, PLAY_END, POSITIONS_PER_HAND = 46, 126, 8


class RightmostPlayPolicy(BaselinePolicy):
    """Keep the baseline hand-slot choice; insert at its rightmost legal slot."""

    def act(self, observation: dict, context: dict | None = None) -> int:
        action = super().act(observation, context)
        if PLAY_START <= action < PLAY_END:
            mask = np.asarray(observation["action_mask"], dtype=bool)
            hand_start = PLAY_START + ((action - PLAY_START) // POSITIONS_PER_HAND) * POSITIONS_PER_HAND
            positions = np.flatnonzero(mask[hand_start:hand_start + POSITIONS_PER_HAND])
            if len(positions):
                return int(hand_start + positions[-1])
        return action


def _play(seed: int, agent_id: str, rightmost: bool) -> dict:
    # canary.run validates each selected legal action against the live engine
    # mask and continues until Game.is_over() is true.
    original = canary.BaselinePolicy
    try:
        if rightmost:
            canary.BaselinePolicy = RightmostPlayPolicy
        receipt = canary.run(seed, agent_id, "baseline")
    finally:
        canary.BaselinePolicy = original
    receipt["policy"] = VERSION if rightmost else "baseline-leftmost-v1"
    receipt["strategy_version"] = receipt["policy"]
    receipt["illegal_actions"] = 0  # canary raises before step on an illegal action
    validate(receipt)
    return receipt


def _save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _stats(records: list[dict]) -> dict:
    ranks = [r["placements"][0] for r in records]
    return {
        "n": len(ranks),
        "ranks": ranks,
        "mean_rank": statistics.mean(ranks),
        "top4_rate": sum(r <= 4 for r in ranks) / len(ranks),
        "win_rate": sum(r == 1 for r in ranks) / len(ranks),
        "decisions": [r["decisions"] for r in records],
        "truncated_combats": sum(r["truncated_combats"] for r in records),
        "turn_limit_end_count": sum(bool(r["turn_limit_end"]) for r in records),
    }


def run(agent_id: str, seed_start: int, games: int, base_dir: Path = Path(".")) -> dict:
    if not agent_id.startswith("s-") or "/" in agent_id or not 1 <= games <= 20:
        raise ValueError("Invalid session ID or game count")
    baseline, candidate = [], []
    experiment_dir = base_dir / "experiments" / agent_id
    session_dir = base_dir / "research" / "sessions" / agent_id
    knowledge_file = base_dir / "research" / "knowledge" / "proposals" / f"{agent_id}-001.md"
    for i in range(games):
        seed = seed_start + i
        # Same seeded environment, seat 0, seven official bot_play opponents.
        control = _play(seed, agent_id + "-control", False)
        changed = _play(seed, agent_id, True)
        baseline.append(control)
        candidate.append(changed)
        _save(experiment_dir / "controls" / f"baseline-{seed}.json", control)
        _save(experiment_dir / f"001-{seed}.json", changed)

    bs, cs = _stats(baseline), _stats(candidate)
    deltas = [a-b for a,b in zip(cs["ranks"], bs["ranks"])]
    report = {
        "schema": 1,
        "session_id": agent_id,
        "round": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed_start": seed_start,
        "seeds": list(range(seed_start, seed_start + games)),
        "engine": "TavernGym 1.1.0",
        "engine_source_hash": ENGINE_HASH,
        "upstream_commit": UPSTREAM_COMMIT,
        "patch_sha256": PATCH_SHA256,
        "contract": {"features":4017, "cards":447, "actions":245},
        "base_commit": "6ac59235b8238196a0e6462de77b72413c829372",
        "run_commit": os.environ.get("GITHUB_SHA", ""),
        "workflow_run": os.environ.get("GITHUB_RUN_ID", ""),
        "control": bs,
        "candidate": cs,
        "paired_rank_delta_candidate_minus_control": deltas,
        "mean_rank_delta": statistics.mean(deltas),
        "gradient_training_steps": 0,
        "tuning": "4+ seeded paired full games, position-parameter ablation",
        "decision_rule": "lower mean rank wins descriptively; no significance claim from small n",
        "checkpoint": None,
        "checkpoint_recovery": "None: deterministic hand-position ablation; no learned weights",
    }
    _save(session_dir / "comparison.json", report)

    run_id = report["workflow_run"] or "unknown"
    url = f"https://github.com/sstxww/reinforcement-learning/actions/runs/{run_id}" if run_id != "unknown" else "not available"
    changed = "better" if report["mean_rank_delta"] < 0 else "worse" if report["mean_rank_delta"] > 0 else "tied"
    branch = f"agent/{agent_id}/optimization-001"
    round_text = f"""# Round 001 — rightmost placement ablation

- Session: `{agent_id}`
- Start: `main@{report['base_commit']}`
- Branch: `{branch}`
- Hypothesis: for the *same first playable hand slot*, choosing the rightmost legal board insertion slot instead of the leftmost changes attack order and could improve mean finishing rank.
- Prior work: main README, AGENTS, PROJECT_BACKGROUND, SESSION_PROTOCOL and knowledge index. Four open, unmerged PRs cover economy, learning, evaluation and infrastructure; no merged main session evidence existed at kickoff. Their observations are not treated as verified improvements.
- Changed code: new `tavern_ai/placement_probe.py` and `tests/test_placement_probe.py`; no change to shared `baseline.py`, `canary.py`, or training files.
- Reproduction: `python -m tavern_ai.placement_probe --agent-id {agent_id} --seed-start {seed_start} --games {games}`.
- Environment: genuine TavernGym 1.1.0, source fingerprint `{ENGINE_HASH}`, upstream `{UPSTREAM_COMMIT}`, patch SHA256 `{PATCH_SHA256}`; observe2 floats 4017, cards 447, mask 245.
- Tuning budget: {games} fixed seed pairs ({games*2} full eight-seat matches), gradient PPO training steps **0**. This is a discrete strategy-parameter ablation, not PPO weight training.
- Execution: {url}
- Controlled candidate first match: `experiments/{agent_id}/001-{seed_start}.json`; full results and control receipts in the same session folders.
- All game receipts were generated from `canary.run` using `Game.is_over()` and validated with `validate`; masks are tested before each step. Games reaching engine-protective truncation would fail validation.
- Ranks (seat 0, lower better): control `{bs['ranks']}`; candidate `{cs['ranks']}`.
- Mean rank: control **{bs['mean_rank']:.3f}**, candidate **{cs['mean_rank']:.3f}**; candidate-control delta **{report['mean_rank_delta']:+.3f}** ({changed} descriptively).
- Top-four: control {bs['top4_rate']:.1%}, candidate {cs['top4_rate']:.1%}; win: control {bs['win_rate']:.1%}, candidate {cs['win_rate']:.1%}.
- Paired deltas: `{deltas}`; sample is too small to infer a true strength gain. Seeds may remain noisy despite pairing.
- Action count: control `{bs['decisions']}`, candidate `{cs['decisions']}`; simulator protective truncations: control {bs['truncated_combats']} / candidate {cs['truncated_combats']}; illegal actions 0 by checked-mask execution.
- Artifacts: compact receipts + comparison.json committed; no model or checkpoint created; temporary engine build and pip caches excluded from Git.
- Failure modes: changing only insertion position may not fix weak card valuation and economy; composition-dependent effects are unmodeled. No actual TavernArena ranked games.
- Next step: validate on 30+ fresh paired seeds with bootstrap confidence intervals; if promising, condition insertion on board state or minion stats rather than universal rightmost.
- PR: to be added after experiment commit; do not merge without CI.
"""
    status = f"""# Session status — {agent_id}

- Round: 001 (completed real paired evaluation)
- Branch: `{branch}`
- Base commit: `{report['base_commit']}`; experiment run commit: `{report['run_commit']}`
- PR: pending creation/review after Actions completion.
- Algorithm: rightmost legal Play insertion for first baseline-selected hand slot (deterministic rule, no model).
- Completed optimizer/PPO steps: **0**; actually completed {2*games} full TavernGym games ({games} control + {games} candidate).
- Verified candidate mean rank: **{cs['mean_rank']:.3f}** across {games} seeds (first seat rank **{cs['ranks'][0]}**), no significance claim.
- Model checkpoint: **none**; restoration: run `python -m tavern_ai.placement_probe --agent-id {agent_id} --seed-start {seed_start} --games {games}` after engine bootstrap.
- Receipts: `experiments/{agent_id}/001-*.json` and `experiments/{agent_id}/controls/*.json`.
- Results: `research/sessions/{agent_id}/comparison.json`.
- Workflow: {url}
- Next step: independent CI, larger seed budget and conditional placement feature study.
"""
    proposal = f"""# Proposal — {agent_id} R001: Play insertion position

**Status: unmerged exploratory evidence; not confirmed stronger.**

- Single isolated change: the same selected hand card enters at the rightmost legal board position instead of the leftmost one. Control and treatment keep all other decisions from main's BaselinePolicy.
- Hypothesis: combat order caused by initial placement may matter enough to affect eight-seat placements.
- TavernGym 1.1.0 / source hash `{ENGINE_HASH}`, observe2 4017/447/245, upstream commit `{UPSTREAM_COMMIT}`.
- Genuine evidence: {games} same-seed pairs, {games*2} complete real TavernGym games; run {url}; full receipts in `experiments/{agent_id}/`, validated with engine legality masks.
- Control ranks: {bs['ranks']}; rightmost ranks: {cs['ranks']}.
- Mean ranks: {bs['mean_rank']:.3f} vs {cs['mean_rank']:.3f}; delta {report['mean_rank_delta']:+.3f}, so the treatment is {changed} on this very small sample, **not** a proven win.
- Effective/ineffective: only the observed sample effect is known; no statistically validated success, failure or generalizability can be asserted.
- Limitations: only scripted bot opponents, identical seeding need not guarantee identical downstream RNG usage after divergent actions; unknown board compositions; no card values; no PPO step or checkpoint.
- Recommendation: retain as experimental candidate only; compare on >=30 held-out seeds and estimate paired bootstrap intervals. Do not replace shared baseline until supported by stronger evidence.
"""
    for p, content in [(session_dir/"round-001.md",round_text),(session_dir/"STATUS.md",status),(knowledge_file,proposal)]:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--seed-start", type=int, default=31001)
    parser.add_argument("--games", type=int, default=4)
    opts = parser.parse_args()
    result = run(opts.agent_id, opts.seed_start, opts.games)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
