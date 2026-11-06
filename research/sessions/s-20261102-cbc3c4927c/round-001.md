# Round 001 — low-rank card encoder and bounded PPO model policy

## Session / provenance
- Session ID: `s-20261102-cbc3c4927c`.
- Branch: `agent/s-20261102-cbc3c4927c/optimization-001`; base main SHA: `6ac59235b8238196a0e6462de77b72413c829372`.
- Engine: real TavernGym `1.1.0`, source hash `6d8712c93022ba11`, 4017 float features, 447 card slots, 245 masked actions, 3984 card IDs.
- Upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Read reference docs: `README.md`, `AGENTS.md`, `docs/PROJECT_BACKGROUND.md`, `docs/SESSION_PROTOCOL.md`, `research/knowledge/README.md`, empty main session/proposal directories; open PRs #6-#9; successful and failed Actions. Avoid PR #6 strategy, #7 evaluation, #8 infrastructure, #9 learning file sets.

## Falsifiable hypothesis and changes
Replacing the position-aware card projection from `3576 -> 128` with a low-rank `3576 -> 64 -> 128` card tower reduces card parameters by at least 40% without breaking PPO input/output, masked actions, or the ability to finish full games when an explicit per-turn action cap is applied.

Modified `tavern_ai/model.py`; added `scripts/benchmark_card_encoder.py`, tests, `tavern_ai/safe_model_canary.py` and `.github/workflows/experiment-s-20261102-cbc3c4927c.yml`. No code outside this branch was modified. Do not merge automatically: a smaller model is not necessarily a stronger policy.

## Reproduction
- Dedicated GitHub runs: [first failure 41413377072](https://github.com/sstxww/reinforcement-learning/actions/runs/41413377072), [fixed successful 41414184717](https://github.com/sstxww/reinforcement-learning/actions/runs/41414184717).
- Engine install: `bash scripts/bootstrap_engine.sh`, then `python -m tavern_ai.contract`.
- Tests: `python -m pytest`; full torch tests only under `pip install -e '.[train,test]'`.
- Encoder benchmark: `python scripts/benchmark_card_encoder.py --out reports/s-20261102-cbc3c4927c/001-encoder-benchmark.json`, single CPU thread, batch16, seed22020, 8 warmups +40 timed batches.
- PPO run (each independent attempt): `python -m tavern_ai.train --steps 128 --seed 22021 --out checkpoints/s-20261102-cbc3c4927c/model.zip`. n_steps128, batch64, n_epochs4, gamma0.99, GAE lambda0.95, lr 3e-4, ent_coef0.01, numeric 192/128, policy/value heads each128.
- Hard limits: 1200s training process, 1000s full-match process; workflow 65min. Second training reported 4 seconds wall time excluding setup/engine.
- Actual training total this session: 128 steps in failed-match run + 128 fresh steps in fixed run = **256 executed steps**. Final model itself has 128 steps; **not** a 256-step resumed model.
- Baseline full game: `python -m tavern_ai.canary --agent-id s-20261102-cbc3c4927c --seed 22022 --policy baseline --receipt experiments/s-20261102-cbc3c4927c/001-baseline-22022.json`.
- Final trained-model game: `python -m tavern_ai.safe_model_canary --agent-id s-20261102-cbc3c4927c --seed 22022 --model checkpoints/s-20261102-cbc3c4927c/model.zip --receipt experiments/s-20261102-cbc3c4927c/001-22022.json`.
- Both use pinned real TavernGym, seat0 controlled by own policy, other 7 seats by game.bot_play; all eight placements from Game.placements().

## Actual measures
| Metric | Main V1 | Candidate |
| --- | ---: | ---: |
| Card network parameters | 458,112 | 237,376 |
| Total network parameters | 1,328,448 | 1,107,712 |
| Forward batch16 CPU median (ms), successful run | 0.687101 | 0.608044 |
| Full game policy | Rules baseline | 128-step PPO + end-turn cap64 |
| Controlled seat rank, seed22022 | 6 | 8 |
| Controlled decisions | 59 | 311 |
| Placements | [6,7,5,3,2,8,1,4] | [8,4,5,6,7,3,2,1] |
| Full game completed | yes | yes |
| Forced legal end-turn actions | n/a | 4 |
| Simulator combat truncations | 0 | 0 |
| Turn-limit end | false | false |

Candidate card-network parameters -48.18%, total model -16.62%, inference median -11.5%. Both true full games completed (15 turns each). No illegal action was observed; any illegal model action raises before Game.step. Model SHA256: `2f06972140a40bf04cca6321c5a70198b69d7e60775980e4801f6578df871508`.

## Failure analysis and limits
The first true PPO training SUCCEEDED, but its unguarded model game FAILED to reach `Game.is_over()==True` after 30,000 loop iterations, raising `RuntimeError: Full-game safety limit exceeded`. A near-untrained PPO repeatedly chose legal non-terminal actions. This is an *incomplete model game*, never a receipt. The failure is recorded in [run #41413377072](https://github.com/sstxww/reinforcement-learning/actions/runs/41413377072).

The fix uses legal action0 to end a turn after 64 model decisions in a turn only when mask[0] is True; all interventions are counted and disclosed. The fixed model completed seed22022 with 4 safety interventions. This is a **hybrid safety policy**, not pure PPO. The model ranked 8 vs rules rank 6 on one matched seed; no improvement demonstrated. Sample n=1 offers no statistical inference; comparing a rules policy to a small PPO also does not isolate architecture causality. The rank result is not TavernArena Elo.

## Storage / handoff
- Final isolated checkpoint: [GitHub Actions artifact #13126448465](https://github.com/sstxww/reinforcement-learning/actions/runs/41414184717/artifacts/13126448465), expires **2027-01-31**, NOT permanently retained. Model file within artifact: `checkpoints/s-20261102-cbc3c4927c/model.zip`; metadata: `checkpoints/s-20261102-cbc3c4927c/model.metadata.json`; checksum file `checkpoints/s-20261102-cbc3c4927c/model.sha256`.
- Model hash above identifies retrievable artifact bytes. For recovery, download matching artifact while it exists, verify SHA256, ensure pinned TavernGym, then pass `--resume checkpoints/s-20261102-cbc3c4927c/model.zip` with adjacent metadata to `tavern_ai.train`; recheck architecture/engine before reusing.
- Persistent compact results: `experiments/s-20261102-cbc3c4927c/001-22022.json`, `001-baseline-22022.json`, `reports/s-20261102-cbc3c4927c/001-summary.json`, `001-encoder-benchmark.json`. No large weights, virtualenv, temp rollouts or caches committed.
- PR: created after experiment result commits; link in PR metadata / STATUS update.

## Next hypothesis
The low-rank model is an engineering efficiency win, **not a strength win**. Train old and new architectures at equal budgets (>=10 held-out seeds, distinct training/evaluation seeds), report mean rank, top4%, first-place%, confidence/bootstrapped intervals, training FPS, and proportion of forced endings. Prioritize learning an explicit END_TURN bias or action-budget-aware features to remove safety overrides.
