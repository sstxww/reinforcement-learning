# V5 R001 — fail-closed main training source; concurrent integration review

Session: s-20261102-1e55e01e
Base main: 1afd8297e3c661bee3117ac5301b1ca08d64869b
Branch: agent/s-20261102-1e55e01e/optimization-001
Engine contract: pinned TavernGym 1.1.0 / observe2 / features 4017 / cards 447 / 245 mask actions / source 6d8712c93022ba11.

## P0 integration audit
- Initial query found 75 open PR: 74 Draft and #15 non-Draft but stacked on unmerged #9, not directly mergable into current main. Never bypass review, dependencies, final-head CI or author's Draft gate.
- Main initially db5e23ae8c218808821327d806b05d2604cfadfb with successful push CI 41432038040. During concurrent integration main moved to 1afd8297e3c661bee3117ac5301b1ca08d64869b (PR #102).
- Main already has canonical registry, Release asset verifier, PPO legal-BUY telemetry and HeroPower-Cancel guard. Avoided duplicating these modules and did not merge any third-party PR or modify their branch.
- New PR is deliberately isolated, non-merge-ready until our independent full-game receipt and latest-head CI finish, actual source-weight/optimizer continuation work, and integrator review.

## P1 specific correctness gap
The main shared .github/workflows/train.yml previously downloaded the last successful *expiring* Actions Artifact; on missing or expired Artifact it fell back to randomly initialized model, silently breaking the intended lineage, and it only uploaded another expiring Artifact rather than a durable new Release.

Changes proposed in this branch (not main until merged):
1. Read only an ID/SHA recorded by canonical models/registry.json; never choose an arbitrary remote model or silently start random initialization.
2. Download both model.zip and model.metadata.json from the corresponding durable Release; verify checkpoint SHA256, ZIP/optimizer, pinned engine and actual CPU inference before calling the existing resumed MaskablePPO trainer.
3. Limit main incremental budget to 128..512 steps until model behavior is credible; keep original checkpoint separate from challenger output and assert cumulative timestep increase.
4. Require genuine complete model-controlled eight-seat match and paired baseline evaluation before publishing *unpromoted* candidate Release; redownload both assets to check published bytes. No Champion promotion.
5. On failure, preserve short-lived diagnostic Artifacts (not a durable trained model); fail closed and do not hide low-capability candidate behind fallback.
6. Use existing main-only concurrency to avoid concurrent weekly writes; the workflow is not allowed to run from a PR branch.

Offline tests added: tests/test_v5_train_release_source_1e55e01e.py. Independent branch full-game proof workflow: .github/workflows/v5-release-gate-s-20261102-1e55e01e.yml. Actual Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41450170855 (queued when this note was written). Do not claim this job passed until its final status is observed. No model bytes were downloaded or trained in this chat.

## P2 verified rank-8 evidence
- Registered latest V5 1408-step experimental Release v5-s-20261102-68099929-1408-41428692617 had three heldout rank-8 games; comparison baseline ranks [6,8,8]. This is unpromoted; no Champion.
- PR #103 reports 521 BUY-legal decision opportunities and 0 model buys (n=3 guarded games), despite mask allowing Buy.
- Stacked PR #107 forces 46 real purchases over three more games with all three still rank eighth, with extensive Play/Cancel loops and increased guard-forced ends; this negative intervention disconfirms “just buy more” as a sufficient solution, not an optimizer root-cause proof.
- New issue comment: https://github.com/sstxww/reinforcement-learning/issues/78#issuecomment-6577815450
- No competitive performance improvement, new PPO steps, or new model weights are claimed in this R001.

## Failure/limitation and next review gates
- Current conversation/container cannot fetch GitHub remotely or install pinned engine, so no local TavernGym game was simulated. A real bounded GitHub Actions full-game run was requested; only its completed result and committed receipt count as validation.
- Run the exact-head branch CI, verify true receipt and workflow YAML/security review. If CI fails, read actual logs, make at most two substantial fixes, preserve evidence.
- Confirm main SHA again before any merge; owner/integrator must assess broad shared train.yml change and Release write scope. Draft PR intentionally holds this gate.
- Once safe and merged, run bounded 128-step Release-backed main training. Do not scale if model remains rank 8 or relies on guard. No ranked Arena is authorized.

No other sessions' files, results, or checkpoints were modified. No main write. No new Champion.
