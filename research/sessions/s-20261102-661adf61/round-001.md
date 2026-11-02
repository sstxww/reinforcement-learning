# Round 001 — real masked behavior-cloning pilot (completed, RETEST)

## A. Provenance
SESSION_ID `s-20261102-661adf61` | Branch `agent/s-20261102-661adf61/optimization-001` | Base main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d` | Experiment source SHA `3e093f073f8f461725ce2cff20edb98e600f9179` | [Actions run 41419937945](https://github.com/sstxww/reinforcement-learning/actions/runs/41419937945): **success** (all steps). Latest branch commit/PR/CI to be checked separately.

## B. Prior knowledge and mechanism study
Main `research/knowledge/INCIDENTS-20261102.md`: some PPO checkpoints fail to complete games; Release uploads sometimes 403. Upstream TavernGym `docs/TAVERNGYM.md` confirms action bands and observable-only interface; detail in `mechanisms-001.md`. Concurrent #15 V2 PPO: 1,280 real PPO steps, held-out four ranks all 8, Baseline mean 7.25; #60 PPO telemetry: three held-out ranks 8/8/8 with zero purchase actions. These are **unmerged PR evidence, not formal main conclusions**.

## C. Hypothesis
A legality-masked neural policy may learn basic action choices from the simple deterministic `BaselinePolicy` more effectively than training a random PPO actor. A high supervised accuracy is a necessary *imitation* signal, not evidence of improved game strategy. The teacher uses only `observe2(0)`, `legal_mask(0)`, turn and its own action count; the student uses only public feature/card tensors and legal masks. Seven opponent seats are run by the real TavernGym scripted bot API.

## D. Actual model and training
- Engine: pinned TavernGym 1.1.0 source hash `6d8712c93022ba11`; upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`; 4,017 numeric features, 447 card slots, 245 actions, 3,984 vocabulary entries.
- Teacher data: **3 fully completed eight-seat real games**, seeds 65101–65103, **128 labeled seat-0 states**, teacher placements [6,8,8]. Data was generated in the workflow; no fake/synthetic samples.
- Model: 8-dimensional card embedding, two 96-dim branches, 128-unit fusion, 245 masked logits; CPU, Adam LR 0.001, minibatch 64, **80 genuine supervised optimizer updates**, fixed seed 65100. PPO timesteps: **0**.
- Training cross-entropy: first minibatch 3.2320580482, final minibatch 0.1458246261; this is not rank reward and not a held-out loss measurement.
- Exact model SHA256 `b77aab475a502dacd2c036f4df87cbadd4656299bf5baaa13f16569b04699cd8`.
- Recovery: temporary [Actions artifact #13128524452](https://github.com/sstxww/reinforcement-learning/actions/runs/41419937945) named `bc-session-s-20261102-661adf61`, includes `bc-model.pt` and `report.json`, expires **2026-12-02 09:24:05 UTC**. NOT independently release-recovered or persistent beyond expiration.

## E. Real complete eight-seat games and held-out comparison
All **eight** games completed without truncated combat or turn-limit end: 3 training teacher games, 2 held-out teacher games, 1 raw BC game and 2 guarded BC games. Exact receipts: `experiments/s-20261102-661adf61/001-*.json` and combined compact report `reports/s-20261102-661adf61/001-masked-bc.json`; run evidence above.

| Policy | Independent seeds | Ranks | Mean | Top 4 | First | Forced end turns |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Teacher baseline | 65901, 65902 | 8, 7 | 7.50 | 0% | 0% | 0 |
| Raw BC | 65901 | 7 | 7.00 | 0% | 0% | 0 |
| Guarded BC | 65901, 65902 | 7, 7 | 7.00 | 0% | 0% | 0 |

Held-out action imitation: 37/41=90.24% and 53/65=81.54% on separately generated teacher states. No rank CI estimated for n=2; observed paired mean difference -0.5 is **not statistically supported**. On those two completed guarded games the safety rule never activated, but the second seed was not independently run under raw labeling. Only one explicitly raw model game is verified.

## F. Faults, interpretation, and integration
No observed workflow/test/game failure in this run; prevention tests ensure mask enforcement and raw/guarded metric separation. The model imitates a demonstrably weak rule teacher and remains rank 7; high behavior-cloning accuracy can be actively misleading as a quality signal. **RETEST** only; do not promote to Champion or present as 15000-MMR-level. Review only the isolated code/tests and real receipts; never merge a new best checkpoint based on this n=2 pilot.

## G. Next hypothesis
Collect per-action-band decision statistics and no-progress recurrence telemetry, then run more *raw* held-out seeds, ideally seat-rotated, to learn whether cloned policy can buy, place and upgrade coherently. If raw BC consistently completes but remains rank 7–8, focus on better verified teacher data and strategic card-value labels rather than extra imitation epochs. The current teacher's turn budget was not provided as model input, so overfitting to frequent End Turn choices is a specific concern.

## H. Reproduction
`python -m pytest tests/test_bc_session_661adf61.py`; `bash scripts/bootstrap_engine.sh`; `python -m tavern_ai.bc_session_661adf61 --updates 80 --outdir experiments/s-20261102-661adf61`. The run is fully bounded; do not launch looped retries or share checkpoint names.
