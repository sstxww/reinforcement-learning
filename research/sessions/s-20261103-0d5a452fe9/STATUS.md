# V7 session s-20261103-0d5a452fe9

- SESSION_ID: s-20261103-0d5a452fe9
- ROUND: 001
- TASK_KEY: audit/main-direct-merge-enforcement
- ROLE: P0 REPAIRER / REVIEWER (not INTEGRATOR)
- STATUS: running; isolated branch; **no global task claim** and **no merge lease**; not exclusive.
- BASE_MAIN_SHA: c1b828734527bae6141805581693d890cc3bff94
- Branch: agent/s-20261103-0d5a452fe9/optimization-001
- Read V7 TXT: complete 32,014 bytes; latest Gmail V7.
- Reused: Issue #182 (observed CAS bypass), PR #185 (proposed cooperative serial integration), PR #164 (historical concurrent merge), current main AGENTS.md / CI / model registry.
- Implemented: isolated, stdlib-only read-only branch enforcement probe, negative tests and one-shot full-match workflow; no shared merge, trainer, registry or evaluator files touched.
- Main safety observation: GitHub branch API main@c1b828734527bae6141805581693d890cc3bff94 returned `protected=false`, protection disabled, and repository rulesets list empty. Direct merge from independent sessions cannot be excluded.
- Recorded official source checkpoint: unpromoted 1408-step V5 Release v5-s-20261102-68099929-1408-41428692617; SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632; not loaded here.
- Actual PPO steps: 0. New checkpoint/Release: none. Best/Champion promotion: none.
- Real game: baseline-only TavernGym seed 99681, seat 0 with seven bots is pending branch Actions result; do not claim placement or completion in advance. Raw model games: 0.
- Merge calls: 0. Integrated PRs by this session: 0.
- Next action: inspect latest exact-head Actions test + genuine original eight-seat receipt; only mark ready after authentic evidence. Integrator must establish enforced global merge entry (not just workflow concurrency) and independent review before any merge.

## Verified git evidence / exact next actions (updated after PR creation)
- Current own PR: https://github.com/sstxww/reinforcement-learning/pull/203 (Draft deliberately; original game receipt and exact-head gate pending).
- Own source commit f60c3dc3d6d79edcafa43da326871954a7e40860 (head when PR opened); latest head will change upon this status commit.
- Own one-shot Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41513189439; workflow code head d26b4d7cc96ff5db33bb803a628b0467eae1d996; status QUEUED at inspection, **zero verified baseline games by this session**.
- Own PR exact-head CI https://github.com/sstxww/reinforcement-learning/actions/runs/41513338684, head f60c3dc3d6d79edcafa43da326871954a7e40860; QUEUED when inspected. This CI is stale after this status commit: check new HEAD-specific CI rather than reuse earlier run.
- Independently verified **historical** main@c1b828734527bae6141805581693d890cc3bff94 CI https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964 completed/success. This is not our branch CI or merge.
- Independent read-only review evidence posted on PR #185 (discussion ID 6586868489): no enforced one-writer merge; do not treat workflow concurrency as global exclusivity.
- Previously registered model source Release actually lists model.zip (17,525,156 bytes) plus model.metadata.json; *our session did not download or run that checkpoint*.
- READY gate: retrieve **original own** baseline artifact from #41513189439 and verify seed/seat/completion/permutation; commit exact receipt under experiments/s-20261103-0d5a452fe9/001-99681.json, then recheck HEAD-specific PR CI and review. If a run is stuck queued, log it as infrastructure blocked and do not invent a game.
- MERGE gate: main remains unprotected per REST. No globally exclusive authority or main merge attempted; escalate policy enforcement/one designated integrator. Do not promote model or declare integration from this PR.

## R001 verified execution update — actual completed run (supersedes pending language above)
- GitHub Actions live run https://github.com/sstxww/reinforcement-learning/actions/runs/41513189439: **completed SUCCESS** on exact workflow commit d26b4d7cc96ff5db33bb803a628b0467eae1d996; audit regression, live API audit, pinned engine install/contract, genuine full eight-seat baseline canary and artifact upload each succeeded.
- Original Artifact ID **13173887720** downloaded and ZIP extracted. Original receipt SHA256 `23fadd89421f5eaa93f05c257ede7d472d886daec876e1aa0c28ace700b4795e` (518 bytes); persisted unmodified as `experiments/s-20261103-0d5a452fe9/001-99681.json` in commit `270e639cddde3113cfa602df503d7eb819d5fe61`.
- **Real original baseline-only game**: seed 99681, controlled seat 0, seven scripted bots, TavernGym 1.1.0, source hash 6d8712c93022ba11, completed=true, placements [8,4,2,3,6,5,1,7], rank 8, turns 13, decisions 40, truncated_combats=0, turn_limit_end=false. Pure PPO games **0**; baseline is NOT model strength evidence. New PPO steps **0**; model/optimizer/release **none**; paired evaluation sample n=0 (not performed).
- Original live main enforcement audit SHA256 `b304b6f1a69649e31616c2559fc714fe0c7e4f6575295eb84e6f592e6cdc2fac` (340 bytes), persisted as `reports/s-20261103-0d5a452fe9/001-main-enforcement.json` in commit `517a05f6a8fda53984586290dcc72703a64a6ebe`. Verdict **BLOCKED_UNPROTECTED_MAIN**, same exact observed main c1b828734527bae6141805581693d890cc3bff94.
- Prior PR CI https://github.com/sstxww/reinforcement-learning/actions/runs/41513338684 failed only at required own receipt gate: pytest 395 passed, 1 skipped; its worktree had no original receipt yet, so pinned full-game CI was skipped. See `failures/001-missing-receipt.md`. This exact failure was fixed by committing the genuine original Artifact, **not** by weakening validator.
- PR: https://github.com/sstxww/reinforcement-learning/pull/203 ; status at this update **Draft** until final exact-head PR CI has finished and independent review is verified. The PR's previous run is stale after the new receipt/status commits; evaluate only the latest matching head SHA.
- All other historical PRs attributed to original sessions; merged PRs **by this session: 0**; no main merge requested because enforceable exclusivity remains absent; main postmerge CI by this session: N/A.
- Next session first action: re-fetch PR #203 HEAD and GitHub CI run; if exact-head CI passes authentic engine canary, mark PR ready for review, then coordinate **one enforced** main integration path with #185/#182; do not use cooperative concurrency alone as global authorization. Recheck protected main and current SHA immediately before future integration.
