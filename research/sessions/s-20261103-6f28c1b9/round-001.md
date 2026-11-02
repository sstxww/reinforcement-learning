# Round 001 — raw 1408-step PPO seat-one falsification

Hypothesis: most existing seat-zero rank-eight PPO evidence might be seat-sensitive. One held-out seed (992310), controlled seat 1, seven stock TavernGym bots, baseline and same pinned 1408-step PPO model are a small falsification probe; no statistical model-strength conclusion is warranted.

Implemented a unique read-only raw-policy seat-1 runner. It rejects weight SHA drift, incompatible engine, invalid masks, nonfinite observations, illegal model actions, incomplete games and a finite 1800-decision guard. No forced end, bot fallback, buy override or placement on failure. Reuses main's baseline seat rotation, engine bootstrap, receipt integrity gate and Release registry instead of changing shared training/registry files. Synthetic regressions test seat attribution and failure semantics; they are NOT real-game receipts.

Starting main c1b828734527bae6141805581693d890cc3bff94. Model: v5-s-20261102-68099929-1408-41428692617 (unpromoted), expected SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632; optimizer reuse not exercised. New PPO training: zero steps; no new checkpoint or Release. Actual isolated Actions run https://github.com/sstxww/reinforcement-learning/actions/runs/41513511752 was QUEUED when inspected; game outputs not yet observed. Preserve genuine game JSON, or a failure record without rank.

Task claim is branch claims/v7/model-seat1-paired-eval. It is not a main lock. Issue #182 documents a global merge exclusion failure. Integration work on PR #185 belongs to another active session. Do not race its merge. No PR merged here.

NEXT: complete Actions run, inspect steps/logs, retrieve original artifact(s), commit genuine evidence, run latest exact-head CI, and allow only an exclusive gate owner to merge. If model fails, report no placement rather than eighth. Further training is conditional on diagnosing action behavior, not blindly spending more steps.
