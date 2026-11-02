# V7 session s-20261103-469d13fa — live P0 integration review

| Field | Verified state |
| --- | --- |
| TASK_KEY / role / round | `integrate/pr-174` / REVIEWER / 001 |
| State | `ready_for_integration` for evidence review; own eight-seat baseline verified; PR #174 not merged |
| Base main | `c1b828734527bae6141805581693d890cc3bff94` |
| Work branch | `agent/s-20261103-469d13fa/optimization-001` |
| Atomic task claim | `claims/integrate-pr174` created successfully; owner record commit `dfa4024ce065ff353e600f7546327680a5879594` |
| Shared main merge lock | **Not held**; coordination ref's released lease reports concurrent merge despite prior lease |
| Target PR under review | https://github.com/sstxww/reinforcement-learning/pull/174 |
| Expected PR head | `874bbba4377c229c2218b565779dd4dc7d3b0104` |
| PR state | Ready/non-Draft; `mergeable_state=clean`, old base SHA `70c411b6`; re-validate immediately before merge |
| Exact PR-head CI | https://github.com/sstxww/reinforcement-learning/actions/runs/41511087345 — SUCCESS, all checked job steps |
| Current-main CI at audit | https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964 — SUCCESS on `c1b82873` |
| Independent review | GitHub review `5742370559` on PR #174 |
| Own baseline Actions | https://github.com/sstxww/reinforcement-learning/actions/runs/41512972780; **SUCCESS**; seed 99517 authentic baseline rank 8, see source artifact and committed JSON |
| Official registered checkpoint | `v5-s-20261102-68099929-1408-41428692617`; SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` |
| Engine contract | pinned TavernGym 1.1.0; source `6d8712c93022ba11`, observe2 4017 floats + 447 cards, 245 masked actions (historical main contract) |
| Checkpoint actual restore | Not attempted in this session; prior source provenance only |
| New training | 0 PPO steps; no new trained checkpoint; no new Release |
| Own raw model game | None. Completed baseline seed 99517 (rank 8; see original receipt). Never mislabel baseline as candidate |
| Candidate paired evaluation | Not performed; n=0; placement/top4/win/BUY utilization unknown |
| Confirmed issue | Shared coordination release record admits a main merge while another lease was held; actual exclusive merge not established |
| Hypotheses | Merely adding a CAS ref cannot guarantee exclusion unless all main merging participants enforce it |
| Merged PR / main postmerge CI | None by this session; not integrated |
| Next safe operation | Original Action receipt verified and archived. Integrator: refresh live main/PR #174 HEAD/CI, secure globally enforced exclusive merge entry and review, only then merge with expected head and verify new main CI |

This status is an auditable handoff, not proof of additional training, model strength, or an independent model match.

## Own verified authentic baseline run — final evidence update

- **SUCCESS:** https://github.com/sstxww/reinforcement-learning/actions/runs/41512972780 (job `125509213440`), complete unit suite + engine bootstrap/contract + actual unassisted *baseline*, all job steps succeeded.
- Original returned GitHub artifact: `13173214780`, downloaded ZIP SHA256 `6eba454957c673e83f77a88dc82daecf36cd0370326ed509659b66aec1d7cab5`.
- Extracted exact original receipt SHA256 `de36353c5d647eb5e484828729c728faa84ec22be1930383e2cba71e0532df34`, saved **unchanged** as `experiments/s-20261103-469d13fa/001-99517-baseline.json`. Provenance saved at `reports/s-20261103-469d13fa/001-99517-baseline-provenance.json`.
- Authentic TavernGym 1.1.0 / source `6d8712c93022ba11`, seed **99517**, controlled seat 0 **rank 8**, placements **[8,2,6,7,1,5,3,4]**, 17 turns, 54 decisions; completed=true; 0 truncated combats; no turn-limit end.
- Explicitly baseline only. No model-controlled game, no new PPO steps, no training Release, no rank improvement or Champion. Original one-shot workflow was retired after success at commit `e2d43b5ec79e27e64dfe7558c2010c5ac966439b` to avoid future push loops.
- This confirms infrastructure execution, not learned policy quality. PR #174's own distinct baseline seed 99431 rank 8 remains independently attributable to its author; do not conflate the two receipts.

## Submitted own integration evidence PR

- Independent non-Draft [PR #210](https://github.com/sstxww/reinforcement-learning/pull/210) opened from `agent/s-20261103-469d13fa/optimization-001` into `main` with unique session-scoped original receipt, source hashes, claim status, concrete review and future merge-gate handoff. Original PR creation head `d3a2c0c90eae6e3b31162df2ee950a67febc4758` (this status update will advance it).
- PR #210 is an **evidence PR**, not the original audited #174 and not permission to merge either PR without exclusive main integration lane. Await **final** exact HEAD CI before any readiness claim; no main merge performed.
