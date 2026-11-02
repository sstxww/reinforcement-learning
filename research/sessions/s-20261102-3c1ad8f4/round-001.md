# V5 Session s-20261102-3c1ad8f4 — Round 001

## Integration first: live GitHub inspection

- Source: complete 27,248-byte AutoTavern-AI V5 Gmail TXT (2026-11-02).
- Repository: only `sstxww/reinforcement-learning`; parent main at branch creation: `1afd8297e3c661bee3117ac5301b1ca08d64869b`.
- Earlier main HEAD `db5e23ae8c218808821327d806b05d2604cfadfb` had completed green CI [41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040). While this session audited PRs, **another integrator** merged [#102](https://github.com/sstxww/reinforcement-learning/pull/102) into main (`1afd8297`). **This session did not merge #102.**
- At subsequent snapshot: 75 open PRs. Only non-Draft [#15](https://github.com/sstxww/reinforcement-learning/pull/15) targets `agent/learning/v1` and explicitly depends on still-Draft [#9](https://github.com/sstxww/reinforcement-learning/pull/9); merging #15 to main now is unsafe. [#8](https://github.com/sstxww/reinforcement-learning/pull/8) remains Draft with merge conflict. Most others Draft/negative or duplicate. No own PR merges.
- Concurrent sessions are implementing Release/optimizer preflight ([#109](https://github.com/sstxww/reinforcement-learning/pull/109)) and purchase overrides ([#107](https://github.com/sstxww/reinforcement-learning/pull/107)); avoid duplicate writes to shared trainer, evaluation, registry or other branches.

## Verified existing model / assessment baseline

- Main registry: **Champion/Best = null**, latest *unpromoted* candidate `v5-s-20261102-68099929-1408-41428692617`, 1,408 cumulative PPO steps, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, heldout [8,8,8]. Release existence + checks are recorded on main; independent optimizer continuation from *published V5 tag* is not established by this session.
- We use the older unpromoted V2 Release `v2-learning-41413557445`, 1,280 steps, SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a` for consistent behavioral diagnosis, NOT a Champion.
- Pinned real TavernGym 1.1.0 / source hash `6d8712c93022ba11`, observe2 floats 4017, cards 447, mask actions 245.

## Eighth-place hypothesis and disconfirming evidence

- Existing main evidence `reports/s-20261102-83d91476/001-buy-opportunity-report.json` demonstrates V2 rank [8,8] with 74 decisions where BUY was mask-legal, **zero BUY selected**, versus baseline 33 BUY and ranks [6,7]. 222 of 248 V2 actions were IDs 1/2 (refresh/freeze). Legal exposure != good opportunity.
- More recent [PR #103](https://github.com/sstxww/reinforcement-learning/pull/103) reports three V2 guarded games with 521 BUY-legal exposures and **zero BUY**, baseline selected 41; all model ranks 8 (guards used 12 times).
- Crucial **negative intervention**: [PR #107](https://github.com/sstxww/reinforcement-learning/pull/107) reports 9 real games (three variant games per seed). Forcing 46 legal BUY actions in three hybrid V2 games **did not improve rank [8,8,8]**, with 18 guard-forced END_TURN actions and repeated PLAY/CANCEL loops. Hence missing purchases are a confirmed symptom but buy-first alone is *not* a demonstrated cure. PRs #103 and #107 are still Draft; cite as provisional not curated knowledge.
- New falsifiable probe: measure before/after *public observe2 projections* on mask-valid refresh/freeze/move actions within one turn, comparing unchanged baseline and V2 on paired seed 87311. Same projected observation is **not** proof of identical internal simulator state. The new diagnostic code never changes the trained policy weights.

## This session's actual GitHub changes

- Branch `agent/s-20261102-3c1ad8f4/optimization-001` based at `1afd8297...`.
- `tavern_ai/transition_audit_3c1ad8f4.py` — bounded, private-policy agnostic public state-delta trace; strict action mask, SHA256 for V2 input, explicit guard labels.
- `tests/test_transition_audit_3c1ad8f4.py` — synthetic regressions for legal opportunity counting, projection changes, guard accounting and illegal action rejection.
- `.github/workflows/transition-audit-s-20261102-3c1ad8f4.yml` — isolated finite Actions job; Release SHA & metadata gate, paired full eight-seat seed 87311, own real receipts and concise telemetry, artifacts on failure.
- Triggered actual job [41450019646](https://github.com/sstxww/reinforcement-learning/actions/runs/41450019646). Run initially QUEUED. **Results are not claimed until the job completes and genuine receipts are committed.**

## Safety, honest accounting, next gates

- New PPO training steps this session: **0**; new trained model and champion promotion: **none**; official ranked Arena matches: **0**.
- Own real completed games: **not yet verified at this document creation**. Do not invent receipts; inspect Actions and repository commits. Candidate-policy games with guard interventions must be labeled guarded.
- Engineering / model quality are separate. Test-only CI cannot assert competitive rank gain. P0 is not fully resolved; P1 resume/optimizer checkpoints overlap work owned by other sessions. Do NOT launch a large PPO batch on a known model that cannot consistently buy, play or progress.
- Next: read actual job status/step logs, remedy errors with at most two meaningful fixes; check complete genuine game receipts, isolate loop failure by action category and observation delta; preserve evidence, open a reviewable Draft PR, and only then plan one small controlled model intervention on a separate round.
