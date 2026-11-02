# s-20261102-fe461d0d R001 — V5 integrated Release continuation gate

## P0 live integration audit
At initial fetch, main was db5e23ae8c218808821327d806b05d2604cfadfb, with 75 open PRs (74 Draft). Latest main CI #41432038040 passed. By branch creation main had advanced to 1afd8297e3c661bee3117ac5301b1ca08d64869b. This change is isolated; no existing agent PR is modified.

PR #15 (only non-Draft) is stacked on open Draft PR #9; do not merge alone. PR #93 CI ran successfully on a four-entry registry while latest main holds five entries, so its count-specific tests will fail once integrated. Posted GitHub PR #93 comment 6577783113 describing the observed conflict.

## P1 exact change
The shared main train.yml restores from a 90-day Artifact and silently starts fresh when unavailable. This branch changes it to manual-only, **strictly requires a canonical registered durable GitHub Release**, verifies both downloaded Release files against the existing digest index, ZIP/optimizer members, and engine contract using main's validators, and refuses unknown, tampered or missing checkpoints. Source model never gets overwritten. After an opt-in run, full model game and paired baseline evaluation gate publication of a uniquely tagged **unpromoted** candidate Release, followed by byte-for-byte re-download check. No auto-Champion, no scheduled bulk training.

Added tavern_ai/release_restore_entry.py and tests/test_release_restore_entry_fe461d0d.py. This is an orchestration integration of existing validators, not another competing registry.

## P2 grounded eighth-place evidence
Canonical latest: unpromoted 1,408-step Release v5-s-20261102-68099929-1408-41428692617. Its three heldout placements were [8,8,8], paired baseline [6,8,8]; no gain established. Other real-game PRs (#91/#103) document 0 actual buys despite masked-legal buy options; this supports a behavioral failure but **not** a proven reward/LR cause. PR #107 reports that forced purchases do not necessarily improve rank. No Champion promotion or large PPO scale-up is justified.

## Genuine execution reporting
Initially this session performed 0 PPO gradient steps, 0 model-only real games and published no weights. Branch CI/Actions must be read before making later claims. Run and receipt fields to be updated from actual execution; do not substitute reported results from other sessions.

## Follow-up gating
Check branch CI and new TavernGym-controlled receipt. If restore or training fails, preserve logs and do not release a broken checkpoint. Review source Release and metadata SHA, ensure output can resume, then review this PR against fresh main and verify postmerge main CI. Research should prioritize legal-buy opportunities, Freeze/Refresh repetition, and guarded vs unguarded action frequencies before enlarging PPO.
