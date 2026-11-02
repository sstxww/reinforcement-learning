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

## Verified R001 true execution (after initial draft)

- Run: [Actions #41450034817](https://github.com/sstxww/reinforcement-learning/actions/runs/41450034817), **completed success**; pinned real TavernGym 1.1.0, source fingerprint `6d8712c93022ba11`. CI status on PR must be checked separately.
- The preexisting canonical latest 1408-step experimental Release `v5-s-20261102-68099929-1408-41428692617` was downloaded, both asset SHA256s matched the canonical asset index, ZIP + optimizer entries checked, actual CPU MaskablePPO loaded. Source checkpoint SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.
- Actual optimizer continuation: `python -m tavern_ai.train --steps 128 --seed 42 --resume checkpoints/model.zip --out checkpoints/candidate.zip`; original total 1408, new total **1536**. New checkpoint SHA256 `c2c456e72164e0819b9793955c10832234f43dfc7bd1da76187e6b912f2c89c2`.
- Full own-seed baseline control `52611` rank **8**, `completed=true`, 14 turns, 36 decisions, placements `[8,3,1,5,2,6,7,4]`; own receipt committed on branch: `experiments/s-20261102-fe461d0d/001-52611.json`.
- Full **candidate-model-only** seed `52612` rank **8**, `completed=true`, 15 turns, 111 decisions, placements `[8,4,2,6,7,3,5,1]`, no combat truncations and no turn-limit ending; own receipt `experiments/s-20261102-fe461d0d/002-52612.json`. This unguarded model controlled the seat with no BaselinePolicy fallback.
- Real heldout paired seed `52614`: candidate rank **8**, baseline rank **8**, delta zero; one seed only, no benefit established. Preserved `reports/s-20261102-fe461d0d/001-paired.json`.
- Persisted model and metadata and the exact game/eval receipts into unpromoted immutable GitHub [Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-fe461d0d-smoke-41450034817-1), then re-downloaded weights and metadata and checked `cmp`. GitHub published asset digests agree with generated files. Game JSON SHA `0194506f33185d86ff34852c981d5f26d288d42a9dfb982c23ebd3afa8fece4f`; paired JSON SHA `10a82980ab31805ef5b4c40cb70b85ec3751d357a14e6d3e1fcb5d13c7bcadcc`.
- Total actual PPO steps by this session: **128**; exact known genuine complete games by own workflow: **4** (one baseline canary, one model canary, one model heldout, one baseline heldout). No policy superiority or Arena result claimed. **Do not automatically add this weak experimental release to canonical latest / Champion**; it remains a durably recoverable unpromoted diagnostic candidate.
- First PR CI [#41450089924](https://github.com/sstxww/reinforcement-learning/actions/runs/41450089924) had 240 offline passes + 1 skipped, then failed the required branch receipt precondition because it ran before our baseline game's bot commit. Its subsequent bot-initiated CI was `action_required` and is not a pass. Retest on latest user-committed head, verify mergeability vs rapidly changing main, and keep PR Draft before merging.

## P2 result, constraints and next iteration

128 additional PPO steps **did not repair** rank-eight on two tested model-seed games (canary 52612 and heldout 52614); the single paired heldout is too small for causal attribution. Stronger independent data in [PR #103](https://github.com/sstxww/reinforcement-learning/pull/103) reported zero buys in 521 masked-legal-buy decisions across three V2 games; the [PR #107](https://github.com/sstxww/reinforcement-learning/pull/107) 46-forced-Buy ablation still ranked eighth and cycled Play↔Cancel. The next one-factor evaluation should log actual public board/hand progress, action family and mask-legal opportunities with guard interventions distinguished. No blind bulk training while those failure modes persist.
