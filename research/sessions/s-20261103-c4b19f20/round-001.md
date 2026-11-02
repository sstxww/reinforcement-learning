# s-20261103-c4b19f20 — Round 001 (V5 integration-first)

## Immutable starting context
- Scope: only sstxww/reinforcement-learning; no writes to upstream, Arena, another agent's branch, shared main trainer or model.
- Started at main HEAD: \`9685cc33c0f05821de3e0a8d2997aedeb3725500\` (after #152 merge).
- TavernGym 1.1.0 / observe2, source hash \`6d8712c93022ba11\`; 4017 float features, 447 card slots, 245 actions.
- Own branch: \`agent/s-20261103-c4b19f20/optimization-001\`; integration scope limited to newly named read-only triage tool/test, own workflow, own receipt, own reports.
- Authoritative request: V5 full TXT Gmail attachment, integration and reliable continuation *before* larger training.

## P0 — real live GitHub inventory, not a guessed number
- Observed 115 open PRs in a live search snapshot, 114 Draft, one non-Draft: #15.
- #15 base is \`agent/learning/v1\` (not main); prerequisite #9 remains Draft. Its exact-head test check was green; this does not clear the dependency or prove model strength. **Do not merge #15 directly to main.**
- #120, #140 and #152 were already merged by *other* agents. No duplicate merge claimed in this session.
- #152's strict eight-seat permutation check is present on main; post-merge main full-match CI #41506832439 finished success on SHA \`9685cc33c0f05821de3e0a8d2997aedeb3725500\`.
- Draft/overlap groups: Release continuation #128/#134/#149 and many others touch shared \`.github/workflows/train.yml\`; paired evaluation #148 and others touch evaluator; #138 touches registry promotion. Do not bulk-merge conflicting versions.
- New deterministic, read-only helper: \`tavern_ai/integration_triage_c4b19f20.py\`. Requires exact-head PR full-match CI; treats Draft, stacked base, action_required, missing CI, stale CI and unknown mergeability as blockers. Even a green result is only *manual-review eligible*, never auto-merge.
- Local offline tests: 9 passed. GitHub PR-head CI must be checked separately.

## P1 — continuation, evaluation, model storage gaps
- Main \`.github/workflows/train.yml\` still resumes from the previous successful \`v1-model\` Actions Artifact and can silently initialize fresh PPO if restore is unavailable. This fails the V5 durable fail-closed requirement.
- Proposed fix order, *not yet merged*: first integrate a reviewed fail-closed resume guard from competing Draft candidates (e.g. #134), then independently audit Release checks/optimizer/asset lineage, then reconcile #149's durable publishing without reintroducing the fallback-to-fresh path.
- Main registry \`models/registry.json\` advertises experimental Latest 1408-step V5 Release \`v5-s-20261102-68099929-1408-41428692617\`, SHA256 \`a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632\`. Registry \`best=null\` and \`champion=null\`; no proven strong Champion. This session did **not** independently download, hash or resume that model.
- #148 proposes evaluator modifications, but overlaps canonical evaluation code and needs comparison with already merged #140; no blind merge.

## Own real complete eight-seat simulated battle
- Isolated push-trigger workflow run: https://github.com/sstxww/reinforcement-learning/actions/runs/41507315887 — **success**.
- Actual source commit: \`dccfb84c6f45b916bc1c2dc677b01649b506f12d\`.
- Receipt: \`experiments/s-20261103-c4b19f20/001-30721.json\`, recovered from actual GitHub Actions artifact #13172675101 (not hand-generated).
- Baseline policy, seed 30721, controlled seat 0, completed true, ranks [7,5,1,6,8,2,4,3], own rank 7, 18 turns, 63 decisions, truncated combats 0, turn_limit_end false. No PPO weights used.
- Only infrastructure smoke. **This session: 0 PPO steps; 0 model-controlled games; 1 baseline eight-seat game; no model claims, no arena games.**

## P2 — current rank-eight evidence and falsifiable hypotheses
- Main registry records Latest V5 independent heldout candidate ranks [8,8,8] vs Baseline [6,8,8] on three seeds: no demonstrated advantage.
- Draft #154 reports one *raw PPO* complete game on seed 99231, rank 8; zero purchases despite 38 states with legal BUY and 42 REFRESH/70 FREEZE; n=1, matched Baseline also rank 8. Treat as reported single-session evidence, not universal causal proof.
- Draft #156 reports a *non-completing* unguarded raw run: 320 own actions but only turn 6, 32 legal-BUY exposures and zero purchases. **This is diagnostic telemetry, not a scored match receipt.**
- Draft #107 describes negative buy-forcing ablation: 46 forced buys without improvement to rank 8. Guard interventions cannot be credited as pure PPO performance.
- Hypotheses to disambiguate: policy distribution collapsed toward free actions; nonprogress loops; legal-mask semantic mismatch; weakness in learned economy/board features; guarded-vs-raw evaluation confounding. Confirm by per-turn legal-opportunity-normalized decision trace and independent matched-seed, no-fallback complete matches before changing PPO hyperparameters.
- Do not call “insufficient training steps” the verified root cause.

## Gate decision and handoff
- No safe direct merge identified in snapshot: sole non-Draft PR #15 is stacked on Draft #9, rest explicitly Draft. Merges done by other sessions remain their work.
- Checkpoint storage / raw PPO behavior gates fail or remain unverified. **No further training launched; no new model produced or promoted**. This is intentional V5 resource protection, not a completed PPO iteration.
- Next integrate after author acknowledgement and exact final-head CI: select ONE fail-closed shared trainer change, resolve Release versus Artifact semantics, rerun true resume and heldout raw model. Protect main and no forced concurrent merges.
- Own PR remains Draft until latest-head CI and own receipt are reviewed; even when CI succeeds, this tool is only a P0 audit scaffold, not a model improvement.
