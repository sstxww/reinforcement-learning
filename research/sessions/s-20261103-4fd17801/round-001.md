# s-20261103-4fd17801 round 001 — V5 integrated-main continuation and rank-eight evidence

## Mission and authorized scope

- Unique session: `s-20261103-4fd17801`, branch `agent/s-20261103-4fd17801/optimization-001`.
- Base main at branch creation: `df07dd23c99079449417fa8e645cf2b6c76b9704`.
- Authorized repository only: `sstxww/reinforcement-learning`. No upstream modifications or Arena play.
- Never merge this branch without independent full-game evidence and exact-head CI. The branch-only workflow is deliberately read-only to GitHub contents; candidate model is temporary artifact only.

## P0 real integration review

- At first scan main `e837e7b445cfb74a84fdb871a4bae4ec9e0ce034`, 114 open PRs, of which 113 Draft; only non-Draft #15 targeted `agent/learning/v1` and required unmerged Draft #9.
- The PR #157 focused default PR inventory capacity 100→250. Inspected full patch, 116-case synthetic pagination regression, receipt seed 93207, and exact-head CI #41508347874 SUCCESS. While reviewing, another concurrent integrator merged #157 to main commit `df07dd23c99079449417fa8e645cf2b6c76b9704`. Verified the default 250 is actually present in main. This session did **not** perform that merge.
- Multiple active Drafts modify Release/restore/evaluation components; no unsafe merge of another owner's unfinished PR was attempted. #157 changed only audit, tests and owner-scoped evidence.
- Branch-start main introduced manual-only, fail-closed registered Release restore in `.github/workflows/train.yml`; older silent initialization route is no longer in current main. End-to-end new Release publishing for newly trained model remains unverified in this session; #121 recorded HTTP 403 on its own publisher.

## P1 verification / bounded experiment (state pending real Actions)

- Workflow: [isolated run #41509213556](https://github.com/sstxww/reinforcement-learning/actions/runs/41509213556), triggered by the workflow commit `26168df0002e103689e471deb3eaba1732956eba`.
- This run **attempts** actual independent registered Release restoration (latest experimental V5 1,408-step), hash+ZIP+CPU load/optimizer preflight, matched seed 97303 baseline and unguarded source PPO with buy-opportunity telemetry, true 128-step PPO continuation, and unassisted candidate full match on seed 97304.
- Model weights, metadata, evidence receipts are backed by a session-named **14-day Artifact**, never called durable storage. No new Champion or model promotion, no upload to ranked Arena.
- **Do not count any step, completed game, receipt, checkpoint or improvement as successful until the run log/artifact validates it.** The run may fail at exact known gates and will preserve partial evidence.

## P2 source-backed baseline facts (not new-session measurements)

- Main `models/registry.json`: Latest unpromoted V5 1,408-step candidate, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; heldout ranks [8,8,8] versus baseline [6,8,8] on same seeds, no Champion.
- Main `reports/s-20261102-68099929/003-buy-opportunity.json`, seed 99128: raw V5 model had **35 legal BUY decision exposures, zero selected BUY**, 37 rerolls and 70 'other' actions, rank8; baseline had 21 legal BUY decision exposures, 14 actual buys, also rank8. These exposures are dependent and not a sample of independently optimal choices.
- Main `reports/s-20261102-83d91476/001-buy-opportunity-report.json`, V2 seeds 45111 and 45112: **74 legal BUY exposures, 0 buys; 222/248 actions were raw IDs 1 or 2; both placements rank8**; baseline ranks 6 and 7.
- Unmerged experiment PR #107 describes three guarded forced-BUY games with 46 purchases and no rank change; treat as negative and unintegrated evidence, not proof of a repaired model.
- **Supported inference:** legal-mask absence is not the sole reason observed V2/V5 purchased zero in those games; the policy repeatedly picked other legal actions. **Not yet proven:** exact reward/feature/optimizer causal root, whether its actions were true no-op cycles, or that forcing BUY alone improves rank. Do not expand PPO on this observational signal.

## Deliverable status

The own isolated run is live, but results are not yet certified in this document. Final-head CI/receipt status, new PPO step count, checkpoint hash/storage state and true model-only rank must be updated from actual evidence before any merge. Until then: **in_progress / not_promotable**.
