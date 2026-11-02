# Round 001 — evidence-calibrated full-game evaluation

## Research hypothesis
Seed-matched comparisons and confidence intervals can reduce false claims of performance gains from 1–3 full eight-seat TavernGym games. A deterministic calculation based on actual completed-game receipts is reproducible, protects against duplicate seeds and reports uncertainty at extreme win/top-four rates.

## Rationale / concurrent work
The `main` evaluation functionality computes point estimates, not uncertainty intervals. Multiple contemporaneous research PRs report short PPO experiments (128–512 steps per arm, sometimes more) without reliable strength gains, so choosing more learning-rate or card-encoder variants would overlap active work. Historical PPO turn-action loops and Release 403 also discourage creating unguarded model jobs. This round does not modify shared train, baseline, canary, model, or evaluation modules.

## Provenance
- Base `main`: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Session `s-20261102-9e68b534`; branch `agent/s-20261102-9e68b534/optimization-001`
- Required TavernGym 1.1.0, source hash `6d8712c93022ba11`, observe2 dimensions 4017 / 447, 245 legal actions.
- New isolated module: `tavern_ai/session_9e68b534_stats.py`
- New regression tests: `tests/test_session_9e68b534_stats.py`
- Unique workflow: `.github/workflows/experiment-s-20261102-9e68b534.yml`
- Local stat tests: 5 passed; live engine and cloud tests pending.

## Planned bounded experiment (NOT YET OBSERVED)
Run four complete seeded baseline-vs-seven-scripted-bots TavernGym games, seeds 392500–392503, with engine verification and receipt validation. Save `experiments/s-20261102-9e68b534/001-<seed>.json` and `research/sessions/s-20261102-9e68b534/round-001-metrics.json`; report actual mean rank, first-place and top-four rate with Wilson intervals, and bootstrap rank confidence interval (4000 seeded resamples). Real engine must reach is_over, no simulator guard. Record actual Actions run URL in metrics.

## Metrics and scientific caveats
- No PPO training (`actual_ppo_train_steps=0`), no model weights and no checkpoint.
- No policy improvement is asserted; this is a baseline uncertainty diagnostic.
- Wilson intervals assume independent games; seed-specific mechanics may violate simple IID assumptions.
- Bootstrap intervals with only 4 games are exploratory; 30 games is a screening flag, not an automatic proof threshold.
- Successful CI baseline match alone must not be described as candidate PPO verification.

## Outcomes / failures
**Pending actual run.** No placement, match result, CI status, PR URL or run ID is fabricated in this note. After running, update with evidence. If blocked, preserve exact error, make at most two meaningful fixes, and mark limitations honestly.

## Next hypothesis
After independent cloud verification, study paired-seed confidence intervals and a held-out sufficiently powered candidate-versus-control design, while keeping neural-network experiments isolated.
