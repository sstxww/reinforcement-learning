# P0 V5 integration triage — s-20261102-9450775f (2026-11-02)

**Scope:** Current GitHub search returned **68 open PRs** at the initial audit, while concurrent merges and new PRs continuously change the count. Initial main `0cd377e475f1adbea6cf12877d30a97bfb0476e1`, later snapshots `f29a0a6e99161aca4163e51427f6bfabbe02f76f` and `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`. Never treat any of these as a stable head after concurrent writes.

This is a prioritized **sampled triage**, not an exhaustive adjudication of all open PR heads and CI checks; every merge requires a fresh head/check/receipt review.

## A — Integration engineering (evidence reviewed; concurrent merges)

- [#43](https://github.com/sstxww/reinforcement-learning/pull/43), seat-rotation infrastructure: non-Draft, real six-engine-game receipts (seats 0/3/6) and passing workflow. It was independently merged by another session during this audit. **No model strength improvement claimed.**
- [#25](https://github.com/sstxww/reinforcement-learning/pull/25), strict receipt integrity: original draft with final-head CI success (head `cc3f2c3c07a2644110a0371fcf5acb1a8c6659c1`, run 41415480128), synthetic adversarial tests and three authentic baseline receipts. It also was merged by a concurrent integrator. We did not touch main.
- [#69](https://github.com/sstxww/reinforcement-learning/pull/69), observation privacy tests, and [#70](https://github.com/sstxww/reinforcement-learning/pull/70), pinned action semantics: potentially valuable, but **Draft** at review. Requires final-head review and confirmation of non-overlap.

## B — Hold for repair/dependency and full gate

- [#8](https://github.com/sstxww/reinforcement-learning/pull/8): major infrastructure/registry candidate, **Draft and mergeable=false** at audit; likely conflicts with newer main. Do not merge blindly.
- [#9](https://github.com/sstxww/reinforcement-learning/pull/9): resumable PPO V1 still **Draft** at audit. Review checkpoint compatibility and true model-game evidence.
- [#15](https://github.com/sstxww/reinforcement-learning/pull/15): V2 PPO continuation explicitly based on PR #9's branch; **merge #9 first** only after verification.
- [#60](https://github.com/sstxww/reinforcement-learning/pull/60): telemetry is stacked on [#51](https://github.com/sstxww/reinforcement-learning/pull/51); do not merge before reviewing its dependency.

## C — Needs larger or harmonized evaluation before policy promotion

- [#46](https://github.com/sstxww/reinforcement-learning/pull/46) + dependent [#57](https://github.com/sstxww/reinforcement-learning/pull/57), purchase-first, no statistically established gain.
- [#44](https://github.com/sstxww/reinforcement-learning/pull/44) + [#59](https://github.com/sstxww/reinforcement-learning/pull/59), seat-sensitive baseline research; avoid interpreting seat-specific small-sample differences as policy improvement.
- [#62](https://github.com/sstxww/reinforcement-learning/pull/62) and [#64](https://github.com/sstxww/reinforcement-learning/pull/64), masked teacher imitation: imitation metrics must not substitute for full-game placement.

## D — Negative/unproven outcomes: preserve diagnosis, not candidate strength

- [#60](https://github.com/sstxww/reinforcement-learning/pull/60): six genuine model games, low-LR candidate 0 BUY and 21 model END_TURN among 36 actions in 3 games, rank 8 in all 3; reference 20 BUY in 875 actions. Evidence of pathological behavior but not causal proof that LR is responsible.
- [#65](https://github.com/sstxww/reinforcement-learning/pull/65) teacher BC transfer REJECT; [#77](https://github.com/sstxww/reinforcement-learning/pull/77) public-board replacement REJECT.
- [#71](https://github.com/sstxww/reinforcement-learning/pull/71) blind-sell ablation worse; [#56](https://github.com/sstxww/reinforcement-learning/pull/56) persistent process pool still slower; [#53](https://github.com/sstxww/reinforcement-learning/pull/53) lower decision cap still all rank 8.
- These are useful **negative research**, not evidence to overwrite Champion.

## E — Duplicated or neighboring mechanism proposals

- [#67](https://github.com/sstxww/reinforcement-learning/pull/67), [#68](https://github.com/sstxww/reinforcement-learning/pull/68), [#70](https://github.com/sstxww/reinforcement-learning/pull/70), and [#75](https://github.com/sstxww/reinforcement-learning/pull/75) all introduce pinned-engine card/mechanics interpretation. Integrator must compare actual schema, compatibility and source proof; do not combine every catalog blindly.
- New V5 checkpoint-audit proposals [#79](https://github.com/sstxww/reinforcement-learning/pull/79), [#80](https://github.com/sstxww/reinforcement-learning/pull/80), [#81](https://github.com/sstxww/reinforcement-learning/pull/81), [#82](https://github.com/sstxww/reinforcement-learning/pull/82) also overlap in concept. This session isolates **behavior telemetry** as a differentiator and does not modify shared checkpoint interfaces.

## Mandatory next gate

Before any further integration: re-read current main and PR head SHA; PR Draft state and author gates; exact-head CI/checks; real receipt and model-only vs fallback evidence; dependencies and overlap; secrets/weight file scan; test resumability; use GitHub PR merge with `expected_head_sha`; verify new main CI succeeds. No reliable exclusive integration lock was present during this fast concurrent period; hence this session did not race others to merge main.
