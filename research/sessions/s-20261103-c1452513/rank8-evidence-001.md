# R001/P2 — rank-eight mechanism diagnosis from authentic engine evidence

**Scope:** this file audits previously recorded real TavernGym outputs; it does not fabricate a new model game or represent correlations as proven causal mechanisms. All candidate data below came from other independent sessions; this session's own Action 41508962915 was a **baseline-only** full eight-seat game, seed 932019, rank 8, so it is an infrastructure gate, not strength evidence.

## (1) No-buy policy collapse is reproducible

- Source PR #154 / Actions 41450329264, published V5 1408-step SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632: raw model (no fallback or forced ends), seed 99231, completed full game, controlled seat rank 8, 122 actions: REFRESH 42, FREEZE 70, BUY 0. BUY was mask-legal on 38 decision exposures. Those exposures are not 38 independent shop states. Full source: reports/s-20261102-a0dea573/001-published-v5-raw-99231.json.
- Independent V2 source reports/s-20261102-83d91476/001-buy-opportunity-report.json: model-only heldout seeds 45111/45112 ranks [8,8], 0 BUY during 74 mask-legal BUY decision exposures; same-seed baseline ranks [6,7] and purchased. These data suggest model policy fails to convert legal shops into board development.

## (2) Blindly forcing BUY does not explain or fix all failures

- Draft #107 (depends on unmerged #103) records 9 real games, 3 seeds comparing baseline/guarded PPO/guarded PPO+legal-BUY override. All three arms ranked [8,8,8] on those seeds. The override executed 46 actual buys but still had repeated Play/Cancel cycles, with reported counts approximately 257/252, 184/175 and 217/214 in three runs.
- Because those experimental policies had guards/interventions, **do not** report their ranks as pure raw PPO evidence. They disprove only the narrow claim that *any* forced buying must repair the observed rank-8 seeds, not the general value of shop decisions.

## (3) Action-state progression is another likely bottleneck

- Existing diagnostic reports/s-20261102-ba09e2d4/002-action-opportunities.json records a **noncompleted**, iteration-bounded V2 model game with ~2,978 HERO_POWER and ~2,977 CANCEL actions at turn 3. Since it never reached Game.is_over(), it has **no placement** and cannot count as a verified finished loss.
- That trace, along with #107, motivates testing whether the legal action family contains mutually canceling/no-economic-progress choices repeatedly selected by greedy MaskablePPO. A repeated action family alone is not proof that observations are identical: the PR #154 evidence reports zero exact same-observation/action repeats on its one complete game.

## (4) Hypotheses and falsification gates

1. **Poor action-family calibration and sparse credit:** for each independently fixed seed, log raw model action family, available gold, tavern shop, board size, Turn, and exact legal masks; report buying **per distinct shop** and board deployment. Compare to raw baseline on the same seed/seat. A zero-BUY pattern across independent seeds would support this.
2. **Non-progress loops:** trace HERO_POWER→CANCEL and PLAY→CANCEL transitions, including resource delta, observation hashes and action masks. Report terminated vs incomplete runs separately. Compare transitions against guarded fallback or purchase intervention without mixing the ranks.
3. **Architecture/learning budget confound:** 1408/1536 training timesteps are small relative to 245 legal-masked actions and 447 card slots. Do not assume that more PPO steps alone helps; the recorded 256→1280 seed-matched replay was [8,8,8,8] vs [8,8,8,8]. Treat bounded 128-step continuation as a **smoke**, not a performance claim.
4. **Formal model selection:** only a candidate-only, complete, genuine eight-seat set of heldout games with fixed independent seeds/seat rotation and a paired statistical comparison can support a gain. No best/champion promotion for a single rank.

## P1/P2 handoff

Address fail-closed registered Release restoration, independent SHA and optimizer checks, separated write-token publishing and persisted byte roundtrip before scaling training. This branch's bounded source-to-1536 experiment workflow is distinct from the manually gated production trainer, has no automatic Best promotion, and records failure honestly if any match/publisher step fails.

## Actual bounded PPO continuation and fail-closed evaluation (2026-11-03)

- Action https://github.com/sstxww/reinforcement-learning/actions/runs/41509707315 executed a genuine registered, hashed, CPU-loaded 1408-step V5 Release -> 128 additional MaskablePPO steps -> 1536-step candidate. Source SHA a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632; new candidate SHA b2b4a1039ca0f5c0e8475646c80996601d26efd081be533972638607c277508d.
- Parent 1408 pure-model heldout seeds 932040/932041 had placements [8,8], paired baseline [6,8]. Source report reports/s-20261103-c1452513/001-parent-paired-932040.json.
- Candidate 1536 raw model completed authentic eight-player seed 932031 rank8, 18 turns, 114 model decisions, no truncated combats. Source receipt experiments/s-20261103-c1452513/002-model-932031.json.
- **FAILURE:** candidate heldout evaluation on planned 932040/932041 aborted with RuntimeError: Full-game safety limit exceeded, before an evaluable pair report could be produced. The failing seed within the batch was not logged, and no candidate heldout rank is claimed.
- Consequently the write-only Release publish job was skipped. The failed-run artifact 13171404727 contains source evaluation JSON, candidate full-game receipt and candidate metadata but **not** the candidate model.zip; therefore these new weights are **not durable** and are NOT ready for promotion. This loss motivates adding a separately quarantined temporary failed-weight Artifact to the production train workflow (without bypassing publish gates).
- Authoritative JSON report reports/s-20261103-c1452513/002-1536-candidate-heldout-failure.json. No Champion/Best. Stop increasing PPO budget until non-progress decision loops are isolated; never count incomplete heldout as an eighth-place completed game.
