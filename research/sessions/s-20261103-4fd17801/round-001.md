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

## Run results and audit resolution (from completed Actions)

Actual run [41509213556](https://github.com/sstxww/reinforcement-learning/actions/runs/41509213556) fully **SUCCEEDED** on original trigger head `26168df0002e103689e471deb3eaba1732956eba`. Pinned TavernGym 1.1.0 source `6d8712c93022ba11`. Tests and engine install succeeded; registered V5 1408-step Release downloaded and passed checked SHA, ZIP/optimizer, metadata, CPU load, inference preflight.

### Original receipts

| Saved receipt | Seed | Policy | Controlled rank | Decisions | Turns | BUY / legal-BUY decisions | Complete |
|---|---:|---|---:|---:|---:|---|---|
| `experiments/s-20261103-4fd17801/001-baseline-97303.json` | 97303 | unassisted baseline | 5 | 49 | 16 | 18 / 25 | yes |
| `experiments/s-20261103-4fd17801/002-source-model-97303.json` | 97303 | unassisted 1408-step PPO | 8 | 106 | 15 | 0 / 23 | yes |
| `experiments/s-20261103-4fd17801/003-candidate-97304.json` | 97304 | unassisted 1536-step PPO | 8 | 120 | 14 | no category telemetry | yes |

All three original JSONs have `completed:true`, zero combat truncation, `turn_limit_end:false`, policy provenance, source workflow SHA and their respective model digests. The original model's action report has 24 rerolls and 70 'other' decisions. The existing diagnostic source originally classified action ID 2 (FREEZE) as 'other'; the narrow patch corrects this category in **future reports only**. Do NOT retroactively claim all historical 70 'other' actions were FREEZE without the full raw action trace.

### Actual continuation and storage

- Trained **128** real extra MaskablePPO environment steps (1408→1536), training seed 97303. Rollout reported `ep_len_mean=92.1`, `ep_rew_mean=-0.981`; these are not competitive rank evidence.
- Parent source digest `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` verified; new ZIP SHA `e9eb78bb100dd2398258d7f7797b7fc589bc3ef7abd0badca34c964823a04e13`, metadata matched the ZIP as separately downloaded from Artifact.
- [Temporary 14-day Artifact 13171409075](https://github.com/sstxww/reinforcement-learning/actions/runs/41509213556/artifacts/13171409075) expires 2026-11-16 19:26:31 UTC; no durable new GitHub Release and no formal Champion/Best. Model index `models/sessions/s-20261103-4fd17801/1536-candidate.json`.
- New model's unassisted real full game was rank **8**. No paired, seat-rotated candidate-vs-parent statistical advantage established. Do not increase training budget; further work should isolate economics/Freeze and action progress.

### Exact targeted bug and integration gate

- Verified `tavern_ai/buy_opportunity_68099929.classify(2)` used to fall to `other`, hiding FREEZE frequency in P2 summary. Fixed source-only action label with dedicated synthetic regression, no modification to PPO policy itself.
- Own scoped CI still must pass against latest main before integration. Other agents' concurrent merges are not attributed to this session. No ranked Arena match.
