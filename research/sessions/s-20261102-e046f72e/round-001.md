# Round 001 — Compact TavernGym extractor and bounded model-game validation

- **SESSION_ID:** `s-20261102-e046f72e`
- **Branch:** `agent/s-20261102-e046f72e/optimization-001`
- **Base main SHA:** `6ac59235b8238196a0e6462de77b72413c829372`
- **Authoring commits:** `3bda97fd6e0606a5ca8c80a5cdbcc42ea37528c3`, `245bfb3a808715c91d62f4f986aa8b1d5175a538`, `727e53f3a005ba9262e6e221e794bc52dc88d96a`
- **Evidence-producing commit:** `28e83970bdcdc76b2b37b17bbe1ea5deea3515f1`
- **PR:** To be linked when opened; see branch's PR against main.
- **Date:** 2026-11-02

## Hypothesis, prior work and isolation

A compact, legal-mask-compatible observation feature extractor will reduce PPO policy
parameter count by at least 30%, and may reduce time spent in `model.learn` by at
least 15%, without corrupting the 4017-float/447-card/245-action observation contract.
This is **not** a win-rate improvement hypothesis.

Consulted main `README.md`, `AGENTS.md`, `docs/PROJECT_BACKGROUND.md`,
`docs/SESSION_PROTOCOL.md`, `research/knowledge/README.md`, source modules
and GitHub Actions. Main had no merged per-session experimental results.
Open draft PRs #6 (economy baseline), #7 (evaluation), #8 (infrastructure),
#9 (PPO training / canary) are **unmerged leads**, not verified improvements.
To avoid file overlap, this session added only `tavern_ai/compact_*.py`,
`tests/test_compact_*.py`, one unique workflow and session-owned evidence.
The shared training workflow, baseline, canary, and main were not edited.

## Simulator and reproducible training

- TavernGym version: **1.1.0**, source hash `6d8712c93022ba11`;
  upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`;
  observe2 patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Runtime-verified: 4017 float features, 447 card indices, 245 legal-masked actions,
  3984 card vocabulary IDs. Initial legal actions: 2 for each model.
- Train seed: `261102`. Match seed: `26110201`. Same 128 PPO steps per
  variant, fresh initialization, 128 rollout steps, batch 64, four epochs,
  learning rate 3e-4, gamma .99, GAE .95, entropy .01, two CPU torch threads.
- Original extractor: 8-d card embedding, 192-wide first numeric layer, 256-d output.
  Compact extractor: 4-d card embedding, 128-wide first numeric layer, 192-d output.
  Policy head architecture otherwise unchanged; same legal-action masks.
- Run: `python -m tavern_ai.compact_experiment --steps 128 --seed 261102 --out outputs/s-20261102-e046f72e`.
- Final training performed **256 actual steps** (128 + 128) in successful run.
  Across three attempts, training succeeded three times, for **768 executed
  (non-cumulative) PPO environment steps**. Each attempt trained new models;
  the final weights each have only 128 training steps.
- Limits: Actions job 65 minutes, training command 25 minutes, each full-game
  command 15 minutes, checkpoints isolated from shared `v1-model`.
- Successful workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41414170876

## Results

| Metric | Original | Compact |
| --- | ---: | ---: |
| Total policy parameters | 1,449,846 | 833,014 |
| Extractor parameters | 1,352,320 | 751,872 |
| Parameter reduction | — | **42.5447%** |
| Final-run actual PPO steps | 128 | 128 |
| Final-run training seconds | 0.268 | 0.200 |
| Final-run model SHA256 | `d9a777f53f2591441b46e1884d5c8a429881d2221bac523d1162fb7c235e4616` | `627c71c1e1dc9007aad4014400ee2414689839c9dbc8151692f2cda8a6934e0b` |

### Three actual paired wall-clock samples (same seed; control always first)

| Actions run | Original learn seconds | Compact learn seconds | Compact faster | Outcome |
| --- | ---: | ---: | ---: | --- |
| [41413064111](https://github.com/sstxww/reinforcement-learning/actions/runs/41413064111) | 0.315 | 0.225 | 28.57% | Candidate game hit 30,000-iteration safety cap |
| [41413715344](https://github.com/sstxww/reinforcement-learning/actions/runs/41413715344) | 0.159 | 0.105 | 33.96% | Model runner rejected workflow's `--policy model` CLI flag |
| [41414170876](https://github.com/sstxww/reinforcement-learning/actions/runs/41414170876) | 0.268 | 0.200 | 25.37% | Both games and evidence commit succeeded |

All three show shorter compact learn times; observed speedups are not yet
causal proof because the original always ran first and may absorb warm-up
costs. Need order-randomized repetitions and multiple seeds before a
performance claim.

### Real full eight-seat game receipts (successful run 41414170876)

- **Candidate receipt:** `experiments/s-20261102-e046f72e/001-26110201.json`.
  Seat zero **rank 8/8**, full placements `[8,7,2,5,4,1,3,6]`,
  13 turns, **518 decisions**, 6 masked-legal forced end-turn actions,
  0 illegal actions, 0 truncated combats, `turn_limit_end=false`,
  `completed=true` from real `Game.is_over()`.
- **Control receipt:** `experiments/s-20261102-e046f72e/control-26110201.json`.
  Seat zero **rank 8/8**, placements `[8,5,3,4,6,2,1,7]`,
  15 turns, 95 decisions, 0 forced end-turns,
  0 illegal actions, 0 truncated combats, `turn_limit_end=false`,
  `completed=true`.
- Mean placement: original 8.0 / compact 8.0 (n=1 per policy).
  Top-four: 0/1 both. First place: 0/1 both.
  **No claim of better gameplay, ELO or win rate is supported.**
  These are independent full matches, **not** CI's unrelated canary.

## Failure lessons and fix

1. Untrained compact PPO repeatedly chose non-ending legal moves in the
   original `canary.py` model mode. The real simulator did not complete
   within 30,000 loop iterations. No receipt was invented; this attempt
   is marked failed. Fixed with a *session-owned* `compact_canary.py`:
   after 80 model actions in the same turn, choose action zero only if
   legal by the actual mask; otherwise use the predicted legal action.
2. Next run failed **before playing** because the new CLI did not accept
   the existing workflow's `--policy model` flag. Added compatible
   argument parsing. Tests passed; third run was fully successful.
3. Candidate needed 6 forced end-turn actions in the successful game.
   This is a real stability warning: raw short-trained policies can
   enter pathological optional-action loops. Treat the guard as
   deployment safety logic, not as evidence that the compact model
   makes better strategic decisions.

## Storage and reproducibility

Successful isolated checkpoint Artifact:
https://github.com/sstxww/reinforcement-learning/actions/runs/41414170876/artifacts/13127575014

Artifact name: `compact-s-20261102-e046f72e`; stored `outputs/s-20261102-e046f72e/control.zip`,
`candidate.zip`, their `*.metadata.json`, and metrics. Expires
**2027-01-01T08:38:46Z**. No verified permanent storage exists;
the model is **not permanently archived**. Exact model SHA256 checksums
appear above and in `research/sessions/s-20261102-e046f72e/training-metrics.json`.

Example recovery before expiry:
```bash
gh run download 41414170876 --repo sstxww/reinforcement-learning \
  --name compact-s-20261102-e046f72e --dir recovered-s-20261102-e046f72e
# Compare checkpoint SHA256 against this log before using it.
```

Temporary Rust build files, pip caches, raw rollout logs, and large
model weights were not added to Git. Retained: code, isolated workflow,
2 true match receipts, concise metrics, round log, status, proposal.

## Reusable conclusions and next round

- The compact model achieved a **verified 42.54% policy parameter reduction**.
- Mask-legal end-turn guard resolved an observed looping failure.
- Three short-run CPU timings favor compact; evidence is **order-biased**.
- No strength gain was observed in n=1 matched-seed games, both rank 8.
- Next: run AB/BA random-order repeats with 5+ independent seeds, then
  compare 20–32 held-out games per variant (mean rank, top-4, first-place
  rates, confidence intervals) and explicitly quantify guard usage.
