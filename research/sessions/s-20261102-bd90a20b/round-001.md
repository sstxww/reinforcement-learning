# Round 001 — non-invasive mask recurrence diagnostic (verified)

- Session: s-20261102-bd90a20b
- Branch: agent/s-20261102-bd90a20b/optimization-001
- Base main SHA: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Source experiment commit: 2e09a49ec75cfb85e085f3a05b8936ef93a0c435
- Evidence commit (Actions bot, own branch): 6a764ca8f3102add85fe913f0a03c695c96b6ddb
- Real run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415948794
- Artifact: https://github.com/sstxww/reinforcement-learning/actions/runs/41415948794/artifacts/13127686579 (expires 2026-12-02; all primary JSON evidence is also committed)
- PR: link recorded in PR metadata when opened

## Hypothesis and reason
Current main incident analysis documents model legal-action loops and a previously incomplete PPO full game. Other concurrent draft PRs modify reward, compact extractor, receipt audit and loop protection. A session-isolated non-mutating observation/mask tracer can reveal recurrence of identical *public* observations and quantize mask/action counts without affecting the tested strategy, useful for future loop investigations.

## Code / method
Added tavern_ai/mask_probe_bd90a20b.py, tests/test_mask_probe_bd90a20b.py and an own-branch-only bounded workflow. BaselinePolicy and engine source are unchanged; observe2 features/cards/mask are hashed only to record repeated public observations. Validity checked against each chosen masked action before calling the actual Game.step. All eight players are simulated by the true TavernGym engine: seat 0 is our **original baseline** and seats 1–7 are seven official scripted bots. For each seed the unchanged tavern_ai.canary.run reruns the same game as an independent paired control.

Engine: TavernGym 1.1.0; source hash 6d8712c93022ba11; pinned upstream commit fb61201a557ddd36a411cf44aac51ce4d9b606ce; patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0. Contract: 4017 float features, 447 int card slots, 245 legal-masked actions.

This is a pure engineering diagnostics experiment; **no PPO training** (0 steps), no model weights, checkpoint, new policy, model hash or training parameters. There is no Best/Candidate/Latest model from this session. GitHub Actions limits run time to 45 minutes. Python unit tests passed, engine installation/verification succeeded, actual six full games and evidence write succeeded.

## Actual genuine game evidence
Source: https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261102-bd90a20b/optimization-001/reports/s-20261102-bd90a20b/001-metrics.json

| Seed | Seat-0 rank | All 8 placements | Seat-0 decisions | Turns | Mask checks | Same as control |
|---|---:|---|---:|---:|---:|---|
| 48101 | 8 | [8,1,6,3,5,2,4,7] | 34 | 14 | 34 | Yes |
| 48102 | 7 | [7,1,5,3,2,8,6,4] | 44 | 15 | 44 | Yes |
| 48103 | 5 | [5,3,8,1,4,2,7,6] | 49 | 14 | 49 | Yes |

Every pair genuinely reached Game.is_over()==True with completed=true, 0 truncated combats, turn_limit_end=false, and mask checks covering all 127 seat-0 decisions. No illegal action was detected. All 3 instrumented games exactly match original baseline on placements, turns, decisions, combat truncation and turn-limit flags.

Mean rank: 6.6667; first-place rate 0/3 = 0%; top-four rate 0/3 = 0%. These numbers describe a tiny sample of **baseline** games, NOT learned-model strength.

Action-ID histograms and legal-mask count statistics live in the metrics file, not only chat. Across these three games there were **0 repeated identical public-observation+mask hashes within a turn**. This does not disprove PPO loops: the tested policy is a different, deterministic baseline. The hash is intentionally over public observed state, not the full hidden simulator state.

Complete source receipts:
- experiments/s-20261102-bd90a20b/001-48101.json
- experiments/s-20261102-bd90a20b/001-48102.json
- experiments/s-20261102-bd90a20b/001-48103.json
Paired uninstrumented controls:
- experiments/s-20261102-bd90a20b/control-48101.json
- experiments/s-20261102-bd90a20b/control-48102.json
- experiments/s-20261102-bd90a20b/control-48103.json

## Actual faults / limitations
No experiment test, engine, mask, or match failure occurred in successful run #41415948794. An in-progress GitHub job-log fetch briefly returned 404 because the blob was not yet available; this was not a code failure and was not retried. GitHub Actions Artifact expires 2026-12-02; retained committed JSON provides ongoing small data evidence. There is no persistent model checkpoint because no model was trained.

## Conclusion / next hypothesis
Verified the instrumented baseline is observationally non-invasive for three seeded eight-player games. No evidence of competitive gain, as none was attempted. Next isolated hypothesis: run the same tracer against *a trained candidate policy* and determine whether repeated public-state signatures and optional-action counts predict incomplete games, using a hard-bounded game runner and genuinely model-controlled full games. A future PPO-specific pilot must avoid duplicating open loop-guard PRs and cannot reclassify baseline scores as PPO.
