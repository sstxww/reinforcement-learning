# s-20261102-2b0d8089 · Round 001 — signed-log reward ablation

## Question and hypothesis

Can monotone signed-log reward compression reduce the PPO critic's learning instability without damaging decision quality?

**Hypothesis (not confirmed):** on the same pinned TavernGym engine and train seed, `signed_log1p(reward)` may lower the magnitude/variance of critic loss relative to raw reward. This was a small bounded pilot, not a full variance study. The metric collected is only the last-update value loss, so it cannot validate *variance*.

## Prior evidence and isolation

Base `main`: `6ac59235b8238196a0e6462de77b72413c829372`.
Reviewed `README.md`, `AGENTS.md`, `docs/PROJECT_BACKGROUND.md`, `docs/SESSION_PROTOCOL.md`, `research/knowledge/README.md` and `research/sessions/` (main contained only `.gitkeep`). Shared curated knowledge contained no validated optimization results.
Open competing PRs at start: #6 strategy, #7 evaluation, #8 infrastructure, #9 PPO/checkpoints. These are unmerged research leads; this session avoids their code paths (`baseline.py`, `evaluate.py`, `train.py`, `canary.py`, shared workflows).

Session branch: `agent/s-20261102-2b0d8089/optimization-001`. Review PR: [#21](https://github.com/sstxww/reinforcement-learning/pull/21) (draft). Do not merge without integrator review.

## Exact game / training contract

- TavernGym version: **1.1.0**; engine source hash: `6d8712c93022ba11`.
- Upstream commit: `fb61201a557ddd36a411cf44aac51ce4d9b606ce`.
- Patch SHA256: `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Catalog SHA256: `c4c42e6ce5060e1b79fbcd5f4edbf6d17495f0f52690072481d690610f7ef6d7`.
- Observation: 4017 floats / 447 card IDs; legal mask: 245 booleans. Mask support and engine fingerprint checked at runtime.
- Training: MaskablePPO, CPU, `MultiInputPolicy`, `TavernExtractor`; seed `20261102`; two fresh policy runs, **256 timesteps each** (512 successful-run total), `n_steps=128`, `batch_size=64`, `n_epochs=4`, `gamma=0.99`, `gae_lambda=0.95`, `lr=3e-4`, `ent_coef=0.01`, same architecture.
- Evaluation: independent seeds `27001`, `27002`, a controlled player in seat 0 vs seven real game rule bots.
- **Safety caveat:** the very short-trained model loops on non-progressing legal actions. For both trained policies, after 25 seat-0 actions in a turn, the experiment explicitly chooses legal END TURN (action 0), or a legal baseline fallback if END TURN is unavailable. These are `model_bounded_25` hybrid policies, **not unmodified pure PPO**.
- Resource bound: session-specific GitHub Actions workflow, 90 minute timeout, 2 CPU threads, per-run unique 90-day artifact. No shared `train.yml` or shared model state.

Reproduce in isolated Linux / GitHub environment:

```bash
python -m pip install -e '.[train,test]'
python -m pytest
bash scripts/bootstrap_engine.sh
python research/sessions/s-20261102-2b0d8089/run_reward_experiment.py
for f in experiments/s-20261102-2b0d8089/*.json; do [[ "$f" == *summary.json ]] || python -m tavern_ai.validate_receipt "$f"; done
```

## Actual runs, failures and repairs

1. [Run 41412952801](https://github.com/sstxww/reinforcement-learning/actions/runs/41412952801): engine verified, tests passed, 2 × 256 = **512 actual PPO steps**. Two baseline games completed, but the unbounded model-policy canary hit `Full-game safety limit exceeded` after 30,000 driver iterations. The overall run **failed**; no complete trained-model receipt was claimed. Failed-run checkpoint artifact was only temporary.
2. [Run 41413587545](https://github.com/sstxww/reinforcement-learning/actions/runs/41413587545): engine verified; the newly added bounded evaluation script failed Python parsing because a literal backslash-n was used instead of a physical newline. **Zero training steps on that run**.
3. [Run 41414058042](https://github.com/sstxww/reinforcement-learning/actions/runs/41414058042): **SUCCESS**. Runtime contract verified; unit tests passed; **512 actual PPO steps**, six complete eight-seat matches, all six receipts individually validated, no illegal actions or engine protective truncation. Workflow committed generated receipts only to this branch.

**Cumulative executed PPO timesteps across all attempts:** 1024, of which 512 form the complete, comparable successful run. Failed-run checkpoints are not mixed with successful-run results.

## Complete real-game evidence (seat 0 rank)

| Policy | Seed 27001 | Seed 27002 | Mean rank | Top-4 | First |
|---|---:|---:|---:|---:|---:|
| Original rule baseline | 7 (47 decisions) | 6 (46) | 6.5 | 0/2 | 0/2 |
| Raw-reward PPO + legal turn safety | 8 (160; fallback 6) | 7 (212; fallback 8) | 7.5 | 0/2 | 0/2 |
| Signed-log PPO + legal turn safety | 8 (160; fallback 6) | 8 (186; fallback 7) | 8.0 | 0/2 | 0/2 |

All completed, `Game.is_over()==True`, no `truncated_combats`, no `turn_limit_end`, illegal action count zero.

Mandatory own-session completed receipt: `experiments/s-20261102-2b0d8089/001-27001.json`. It contains all eight ranks **[8,2,1,5,6,4,3,7]**, seed 27001, model SHA, engine version, actual decisions and legal turn-safety count. Other independent receipts and `001-summary.json` live under the same isolated directory.

Training final-update diagnostics (not variance / not a population statistic):
- Raw: `train/value_loss=0.0637891`, `train/explained_variance=0.087609`.
- Signed log: `train/value_loss=0.0712823`, `train/explained_variance=-0.526465`.
- Reward compression **did not improve either pilot metric**. With n=2 held-out games per arm and a hybrid fallback controller, **no strength improvement is supported**.

## Code / checkpoint provenance

Code at run head `ca47e15b45bf0b068fa4837f8da15f4927c27b76`. Receipt-only commit `90c9eb41e713b1a180bf3d3835eb69b0acc7486b`.
Files changed: optional `tavern_ai/reward.py`, `tests/test_reward_shaping.py`, independent experiment runner and isolated workflow; no change to default V1 training.

Successful artifact: [reward-s-20261102-2b0d8089-41414058042](https://github.com/sstxww/reinforcement-learning/actions/runs/41414058042/artifacts/13126329809), ID `13126329809`, artifact ZIP SHA256 `3928063cac97699b4f2ba8e3edda6c2df2922ed26abc2c047a55ca01d4701f30`; **expires 2027-01-31** (90-day retention). This is **not permanent model storage**.

Models inside artifact:
- `checkpoints/s-20261102-2b0d8089/raw.zip`, SHA256 `30886ba44bb1067f533f80e89f0b15782fa0fa11de074a0191466efbbf6220f8`.
- `checkpoints/s-20261102-2b0d8089/signed_log.zip`, SHA256 `2a23241582d8d1eb1313ee47dfb562bccef6d1e2a8e8cd956437b985a3014756`.
- `checkpoints/s-20261102-2b0d8089/manifest.json` includes model hashes, step counts and engine version.

To restore before expiry:
```bash
gh run download 41414058042 --repo sstxww/reinforcement-learning \
  --name reward-s-20261102-2b0d8089-41414058042 --dir restored
sha256sum restored/checkpoints/s-20261102-2b0d8089/*.zip
```

Before additional learning, verify the pinned engine and load the ZIP with `MaskablePPO.load(..., env=TavernEnv(...))`. Bit-identical training continuation was **not** tested. No weights, caches, rollout dumps or virtualenv files are stored in Git. Avoid deleting the only stored weights before durable replication.

## Lessons and next experiment

- **Negative result:** signed-log compression is not a justified default reward change on these metrics.
- **Positive engineering finding:** raw masked PPO after just 256 steps can legally stall a full game; an explicit turn-action safety policy restores complete-match reliability while honestly recording fallback intervention.
- **Open issue:** model inferencing path currently lacks explicit full-turn progress control; the competing learning PR owns `canary.py`, so do not modify that file here.
- Next: multi-seed 2k–8k PPO training with a fixed legal progress cap, log full critic loss traces (not only last update) and evaluate ≥20 paired seeds. Any strength claim needs wider confidence intervals and fallback-rate reporting.
