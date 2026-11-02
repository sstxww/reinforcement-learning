# Round 001 — mask recurrence audit

Session: s-20261102-bd90a20b
Branch: agent/s-20261102-bd90a20b/optimization-001
Base main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d

## Hypothesis
A strictly observational mask + observation-fingerprint audit can quantify repeated public observations within a turn and uncover conditions associated with unproductive legal-action loops, **without affecting gameplay**. Compare instrumented baseline vs the original baseline canary at identical seeds. Engineering diagnostic only; not a policy-strength change.

## Previous evidence and scope
Reviewed main README, AGENTS.md, project background, architecture, session protocol, closed loop, knowledge index and 2026-11-02 incident catalog. Existing open PRs independently investigate reward shaping, compact encoders, training/turn-loop guards and receipt integrity. To prevent conflicts, modify only a new session-specific Python module, tests, workflow, receipts, reports and research notes.

TavernGym engine requirement: 1.1.0, source hash 6d8712c93022ba11, pinned commit fb61201a557ddd36a411cf44aac51ce4d9b606ce, observe2 4017 features + 447 cards, 245 actions.

## Method
1. Each of seeds 48101–48103: original baseline seat 0 versus seven official bots, running to Game.is_over().
2. Instrument observe2/mask checks immediately before each seat-0 action; never modify the baseline, mask or engine.
3. Repeat the same seed with unmodified tavern_ai.canary.run. Assert placements, decisions, turns, combat truncation, and turn-limit flags match exactly.
4. Validate both game receipts, store compact per-seed mask/recurrence and action histograms. No model or training is involved (training steps = 0).
5. CI and data-integrity checks are real execution gates; an unrun workflow or missing receipt is **not** evidence.

## Initial status
Pending first real cloud execution. No games, training, comparative outcomes, model hashes, or CI success claimed yet. Workflow is push-only, scoped to this branch and three source paths; evidence-only commits do not retrigger it. Maximum 45 minutes.

## Intended artifacts
- experiments/s-20261102-bd90a20b/001-48101.json through 001-48103.json
- experiments/s-20261102-bd90a20b/control-48101.json through control-48103.json
- reports/s-20261102-bd90a20b/001-metrics.json
- workflow run/job URL and commit hashes after verified execution

## Next hypothesis
If matched replays are identical, inspect which action-ID ranges and repeated-observation counts dominate; future isolated studies can use these diagnostics to evaluate candidate PPO loop guards. This study cannot establish improvement in rank or win rate.
