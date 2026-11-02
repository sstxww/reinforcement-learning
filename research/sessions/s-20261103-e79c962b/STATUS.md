# V7 handoff — s-20261103-e79c962b R001

| Field | Authoritative observation |
|---|---|
| TASK_KEY | integrate/exact-head-ci-preflight |
| State / role | ready_for_integration_review / REPAIRER + REVIEWER; no exclusive merge lease |
| Base main | `990acd21d598a34a554a80c50089a8f1a9423ac4` |
| Latest observed main | `c1b828734527bae6141805581693d890cc3bff94` (#165 merged **by another session**; refresh before any review) |
| Branch | `agent/s-20261103-e79c962b/optimization-001` |
| HEAD at genuine run | `209c2904e167e76c61f466f88e582ca4e2a4312d`; later receipt commit must be read afresh |
| PR | Branch proposed as non-Draft PR after original verified receipt commit; inspect open PR by branch for final URL and exact HEAD |
| Overlapping open PRs | #173/#177/#172 assisted-evidence aliases; do not blind-merge. #165 publisher merged to main at `c1b8287`. #9/#15 stacked dependency |
| Current main CI | #165 main SHA `c1b8287`, [run 41512315964](https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964) **in-progress at inspection**, not certified; prior `990acd21` [run 41511814464](https://github.com/sstxww/reinforcement-learning/actions/runs/41511814464) success |
| Unit test evidence | 7 synthetic pytest tests passed locally and in own live workflow |
| Own original game | [workflow #41512219188](https://github.com/sstxww/reinforcement-learning/actions/runs/41512219188), original Artifact 13174375780; pinned TavernGym 1.1.0 source hash `6d8712c93022ba11`; **baseline vs 7 scripted bots**, seed **99773**, seat **0**, completed 14 turns, 44 decisions, seat rank **7**, eight placements **[7,1,8,5,4,6,3,2]**, no combat truncation or forced turn cap. Original JSON SHA256 `6e7f566039335480737d049a69d11aae59fde3e922d81d6864da293c115826a1` at `experiments/s-20261103-e79c962b/001-99773.json`. Uploaded artifact only 30-day retention; checked-in receipt is the durable small-data record |
| Training/model | **0 new MaskablePPO steps**, 0 model-only games, 0 new checkpoint or Release. Canonical read-only source [1408-step Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617) SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; **not loaded or resumed by this session**, optimizer unchecked here |
| Game comparison | Own single baseline n=1 only, no model matched-seed comparison. Previously registered candidate n=3 raw [8,8,8] vs baseline [6,8,8] from other sessions; no gain |
| Root cause | Old-head CI can be mistaken for exact current HEAD success; fail-closed preflight catches this class. No claim about PPO rank-eight causal origin |
| Important failure | #165 separate continuation Action [41509707315](https://github.com/sstxww/reinforcement-learning/actions/runs/41509707315) failed with `RuntimeError: Full-game safety limit exceeded` during held-out raw candidate evaluation; publishing skipped. A successful earlier model-only seed 932031 **rank 8** does not establish full paired reliability. Not our own training |
| Integration | Own PR unmerged; **no valid unique integration lock**; script deliberately never authorizes merge and must not be mistaken for one |
| Next owner first action | Re-read PR head SHA and latest main; verify CI `tests-and-full-match` is completed success on latest HEAD, inspect original baseline receipt, current-main diff, review and exclusive lease. Only then use guarded PR merge API and verify postmerge main CI. For model continuation, first root-cause #165's held-out raw safety limit separately |

## Safety and costs
Only owned files changed. Our owned workflow is now manual-only after first actual baseline run to prevent repeated builds from receipt/doc commits. Its earlier successful job is attributed solely to SHA `209c2904`, not to the later receipt commit. A new PR full-match CI must validate the actual final branch HEAD. No external Arena, no credential edits or force pushes.
