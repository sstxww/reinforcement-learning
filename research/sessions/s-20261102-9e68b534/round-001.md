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

## Initial bounded experiment plan (subsequently executed and verified)
Run four complete seeded baseline-vs-seven-scripted-bots TavernGym games, seeds 392500–392503, with engine verification and receipt validation. Save `experiments/s-20261102-9e68b534/001-<seed>.json` and `research/sessions/s-20261102-9e68b534/round-001-metrics.json`; report actual mean rank, first-place and top-four rate with Wilson intervals, and bootstrap rank confidence interval (4000 seeded resamples). Real engine must reach is_over, no simulator guard. Record actual Actions run URL in metrics.

## Metrics and scientific caveats
- No PPO training (`actual_ppo_train_steps=0`), no model weights and no checkpoint.
- No policy improvement is asserted; this is a baseline uncertainty diagnostic.
- Wilson intervals assume independent games; seed-specific mechanics may violate simple IID assumptions.
- Bootstrap intervals with only 4 games are exploratory; 30 games is a screening flag, not an automatic proof threshold.
- Successful CI baseline match alone must not be described as candidate PPO verification.

## Outcomes / failures — verified actual execution
- **Succeeded real Actions run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415933253; workflow head at run start `e1015eb6d2dca166e00818f219b9703e0bdaf034`. Test, pinned engine, games, receipt push and Artifact steps all completed successfully.
- **Engine:** TavernGym 1.1.0 hash `6d8712c93022ba11`; all four games genuinely terminated in `Game.is_over()`.
- **Actual game seeds:** 392500,392501,392502,392503; seat0 ranks `[4,6,8,8]`; decisions `[107,50,45,54]` (sum 256); eight-seat placements and per-seed receipts stored in `experiments/s-20261102-9e68b534/`. No illegal masked action, combat truncation or engine turn-limit shutdown.
- **Statistics:** mean rank 6.5; bootstrap rank 95% percentile interval [5,8]; first-place 0/4 (Wilson [0,0.4899]); top4 1/4 (Wilson [0.0456,0.6994]). 4 independent seeds are not enough to establish policy strength.
- **Training/model:** exactly zero PPO training steps; no model or checkpoint. A baseline-only statistics engineering experiment.
- **Evidence commit:** `ab2183ba5ffa912074ac2288db3934c76ecb8751`. Metrics saved in `research/sessions/s-20261102-9e68b534/round-001-metrics.json`.
- **Failures:** none in the completed workflow; a premature job-log fetch returned 404 while it was in progress, not a training or game failure.
- **PR CI:** to be verified separately on the final PR HEAD; do not confuse cloud workflow success with PR CI.

## Next hypothesis
After independent cloud verification, study paired-seed confidence intervals and a held-out sufficiently powered candidate-versus-control design, while keeping neural-network experiments isolated.
