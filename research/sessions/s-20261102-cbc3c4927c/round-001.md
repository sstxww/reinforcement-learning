# Round 001 — position-preserving card bottleneck

- Session: `s-20261102-cbc3c4927c`
- Base commit: `6ac59235b8238196a0e6462de77b72413c829372`
- Branch: `agent/s-20261102-cbc3c4927c/optimization-001`
- Environment: TavernGym 1.1.0, source fingerprint `6d8712c93022ba11`, 4017 float / 447 card / 245 actions; upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Reference prior knowledge: main README, AGENTS, docs/PROJECT_BACKGROUND, docs/SESSION_PROTOCOL, research/knowledge/README; main had no completed session reports/proposals when inspected. PR #6 modifies rule strategy, #7 evaluation, #8 infra, #9 training; code scope intentionally avoids those modules.
- Hypothesis: replace 3576 -> 128 position-aware card projection with 3576 -> 64 -> 128 factorization; reduce card-tower parameter count by >=40% without corrupting feature encoding, and exercise 128-step PPO.
- Code: `tavern_ai/model.py`, `scripts/benchmark_card_encoder.py`, `tests/test_model_bottleneck.py`, independent `.github/workflows/experiment-s-20261102-cbc3c4927c.yml`. Post-failure mitigation adds `tavern_ai/safe_model_canary.py` and focused tests.
- Measured benchmark: card-net params 458,112 -> 237,376 (48.18% less); overall params 1,328,448 -> 1,107,712 (16.62% less). CPU single-thread batch16 median V1 0.68685 ms vs new 0.60985 ms (11.2% less), 40 timed batches, seed 22020. Performance is a microbenchmark, not game strength.
- First independent run: https://github.com/sstxww/reinforcement-learning/actions/runs/41413377072 (FAILED candidate game stage). Unit tests and `python -m tavern_ai.train --steps 128 --seed 22021` SUCCEEDED; final PPO log `total_timesteps=128`. A checkpoint was preserved in run artifact 13126258327, 90-day expiry, not permanent storage.
- True baseline full match: `experiments/s-20261102-cbc3c4927c/001-baseline-22022.json`; seed 22022, seat 0 rank 6, full placements [6,7,5,3,2,8,1,4], 59 decisions, 15 turns, 0 combat truncations and no turn-limit guard. Produced by live original simulator and committed by this session's workflow.
- First **unguarded** trained model game FAILED after full 30,000-loop safety limit; `Game.is_over()` was not reached. This is NOT a completed model game and no receipt was created. Probable cause: near-untrained PPO repeatedly selects legal non-terminal shop actions and never ends a turn.
- Fix/test: for model policy only, after 64 actions in a turn choose action 0 *only when legal*, track the number of forced end turns. Never override masked illegal actions; explicit receipt policy `model-with-legal-end-turn-cap`. This is a safety-assisted model, not a pure learned policy. The original generic canary module is left untouched to avoid PR #9 conflict.
- Plan for rerun: same seed 22021, 128 PPO steps, candidate genuine complete match seed 22022, record model SHA256, end-turn interventions, legality and all eight placements. 1200s training / 1000s full-match timeouts, workflow 65 minutes.
- Strength claim: **no demonstrated improvement**; one seed and unequal policy types cannot isolate the effect of architecture. Ablation on matched training budgets and >=10 held-out seeds required.
- Checkpoint retention: Actions artifacts expire in 90 days. Reproduce from source + seed and training command. Do not treat artifact as permanent.
- Next research: use a PPO training control with the original extractor and matched independent seed runs; evaluate mean rank/Top4, confidence interval and guard intervention rate.
