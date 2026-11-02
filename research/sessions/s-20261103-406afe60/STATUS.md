# V7 session status — s-20261103-406afe60

**1. Claim / stage.** TASK_KEY `policy/raw-ppo-sampling-vs-argmax-99831`; ROUND R001; role EVALUATOR/REPAIRER; **engineering experiment verified, integration pending**. No global atomic task claim or exclusive main-integration lease was obtained; isolation by unique branch and files only, NOT a concurrency lock.

**2. Git identity.** BASE_MAIN_SHA `3a745c6f6a48c65528bcbeb81b8627b8db93f046`. Last main read `c1b828734527bae6141805581693d890cc3bff94` (other integrators merging; refresh before any integration). Own branch `agent/s-20261103-406afe60/optimization-001`; exact successful source experiment source/head SHA `b7260914ab2d7264cc44f1abc41f63bdf7f598f3`; later receipt archive + documentation commits advance own branch; inspect PR's exact current SHA.

**3. Inherited / P0 review.** Read entire 32,014-byte V7 TXT and source `AGENTS.md`, session/closed-loop docs, main registry/trainer/evaluator, open PRs, source issue #158. Other sessions merged PR #166 (main `c5edec2e...`, postmerge Actions SUCCESS #41510861696), PR #176 (main `3a745c6f...`, postmerge Actions SUCCESS #41511419671), and later PR #165. PR #15 still stacked onto Draft #9, not independently mergeable. PR #175 is an ongoing distinct restore-install proposal; never modify its branch. **This session merged zero PRs.**

**4. Own PR and integration gate.** **Non-Draft [PR #204](https://github.com/sstxww/reinforcement-learning/pull/204) OPEN, targeting main**, initially created at head `f8a6bdc2f98441f75fc98e5d6b9382c1facfb1ec` / base `c1b828734527bae6141805581693d890cc3bff94`. An exact-head `CI - full-match gate` run [#41513381132](https://github.com/sstxww/reinforcement-learning/actions/runs/41513381132) was queued on the original PR head; THIS documentation commit will move the head, so final exact-head CI must be refreshed, not claimed from old run. This branch changes only unique code/tests/receipt/workflow/session proposal paths, not canonical train/eval/registry, model weights, main or others' work. No merge attempted without real exclusive entry, review and current-head CI; README/Best/Champion remain untouched. See live PR for latest HEAD SHA.

**5. Checkpoint provenance.** Official registered *unpromoted* 1,408-step source `v5-s-20261102-68099929-1408-41428692617`; Release https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617 ; verified checkpoint SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Source run independently restored Release via canonical SHA/metadata/archive/CPU preflight (not a new optimizer-resume certification). TavernGym 1.1.0 source `6d8712c93022ba11`, observe2 4017 float + 447 card slots, 245 masked actions.

**6. Real training/durability.** **0 newly trained PPO steps**; no new model ZIP or optimizer checkpoint and no new model Release. Historical #176 did a bounded 1408→1536 continuation, retained negative rank-eight evidence. This single-variable inference-selection experiment reuses exactly the same read-only 1408 source weights, does not pretend to fix training, and does not promote Best/Champion.

**7. Original genuine games.** Source Action https://github.com/sstxww/reinforcement-learning/actions/runs/41511916662 **completed SUCCESS** on `b7260914...`; artifact #13174485348 (14-day *temporary*), engine preflight + tests SUCCESS. Original files retrieved, byte-SHA-checked and committed unchanged by one-shot own-branch archive Action https://github.com/sstxww/reinforcement-learning/actions/runs/41512673429 **SUCCESS**. Importer's ephemeral `contents:write` workflow was removed at commit `4b8d76bfb088ef4c2c94f091c0c813d1adca6394` once successful. All seed 99831, seat 0, seven official bots, **completed** `Game.is_over()`, eight-seat rank permutation, no combat truncation, no turn-limit end, zero fallback and forced ends.
 
| Authentic unchanged receipt | Mode | Rank | Turns | Decisions | BUY | Mask-legal BUY decision states | FREEZE | REFRESH |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `experiments/s-20261103-406afe60/001-baseline-99831.json` | baseline | 8 | 15 | 37 | 13 | 20 | 0 | 0 |
| `experiments/s-20261103-406afe60/002-argmax-99831.json` | raw deterministic PPO | 8 | 14 | 125 | 0 | 47 | 70 | 39 |
| `experiments/s-20261103-406afe60/003-sampled-99831.json` | raw stochastic PPO (same SHA) | 8 | 15 | 45 | 4 | 17 | 8 | 10 |

Original source-file SHA256:
- baseline: `4149499bd7fed09b45de93b5801d1b9db4cf9dd10c58df9f3045a7944876a97b`
- argmax: `aba5a0b30e205119c0ce52e06fbc446febf8338cb24c11626410bf5f2abb61dc`
- sampled: `6355ab8757a1d6343480a2438b34f81784fb78adac7635b69efc1703592d3751`

**8. Matched evaluation / uncertainty.** One exploratory same-seed pair and baseline, **n=1 per arm**, rank mean 8 each, top-4 rate 0 and win rate 0 each. BUY/legally exposed decision ratio: baseline 13/20=65%, argmax 0/47=0%, sampled 4/17≈23.5%; correlated sequential mask exposures are *not* independent opportunities. Sampled model still ends 3 times while BUY legal. Model changes its own future state trajectory; no statistical generalization or proven gameplay benefit.

**9. Confirmed vs hypothesis.** Confirmed in these authentic games: direct masked sampling emitted four BUY actions from unchanged weights, while argmax emitted zero and made many FREEZE/REFRESH calls; **all three placed eighth**. Hypothesis only: spreading probability mass across multiple legal BUY IDs may partly explain argmax non-purchasing; neither reward deficiency nor optimality nor rank improvement is established. Separate other action family ID mapping issues may still exist.

**10. Failures / budget.** No own Actions workflow failures in completed original or importer runs. Source checkpoint passed restore and actual game, not a strength gate. No retries, no additional training costs. No credentials, hidden opponent state, ranked Arena, or uploads of model weights into Git.

**11. Integration / main CI.** Our new code/data are **proposed in non-Draft PR #204 and remain branch-only until a verified PR merge**. Other-session successful main checks above do **not** substitute our latest-head PR CI. No own merge SHA, no postmerge main CI, no promotion.

**12. Exact next action for successor/integrator.** Confirm own PR #/latest head SHA; run/inspect its `CI - full-match gate` on the exact final PR HEAD; inspect artifact #13174485348 and import run 41512673429; ensure no overlap with latest main; only an actual exclusive integrator with review/security/main compatibility may merge via PR expected_head_sha. Recheck new main SHA and postmerge CI. Then predeclare at least 3 new held-out seeds/rotated seats for **raw sampled vs raw deterministic** if budget allows, and do not promote while ranks remain eighth. Do not repeat same 128-step continuation without a distinct falsifiable training hypothesis.
