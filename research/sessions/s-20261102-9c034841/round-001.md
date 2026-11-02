# Round 001 — planned-turn buy-before-upgrade paired ablation

## Session and hypothesis
- SESSION_ID: `s-20261102-9c034841`
- Branch: `agent/s-20261102-9c034841/optimization-001`
- Starting main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Evaluated code commit: `fea0eb39e6880b732bc2896ca1a47d126fe79de7`
- Genuine execution: https://github.com/sstxww/reinforcement-learning/actions/runs/41415146112 (**success**)
- Original evidence commit: `760aa6cf51ec58e8b80bcfbea3187f72766baf3b`; PR awaits review and independent CI.
- Hypothesis: on planned tier turns 2,5,7,9,11, purchasing a legal shop minion *instead of an otherwise chosen tier upgrade* during the first three decisions could improve early board survival versus the unchanged baseline. Preserve all higher-priority discover/hand-play decisions.
- Isolation: new dedicated `tavern_ai/upgrade_priority_s_20261102_9c034841.py`, unit tests and one bounded private workflow. Shared `baseline.py`, train.yml, other PRs, models and upstream untouched.

## Historical knowledge and failure
Read main `research/knowledge/INCIDENTS-20261102.md`, session protocol, and open PRs #9/#15/#11/#14/#12/#17/#18. V1 PPO 256-step and V2 1280-step runs produced repeated eighth-place results; longer training alone is not confirmed stronger. Other ongoing experiments cover reward shaping, embeddings, slot bias and placement.
- Original run https://github.com/sstxww/reinforcement-learning/actions/runs/41414939740: 23 tests passed, 1 failed. Root cause was *researcher's inverted reading* of baseline logic: current baseline already prioritizes upgrade over buy on scheduled turns. First candidate was not a meaningful contrast.
- Corrected the experiment and assertions in commit `fea0eb39e6880b732bc2896ca1a47d126fe79de7`, without deleting tests. Successful rerun: 24 tests passed, pinned engine installed, 9 real games completed. See `failures/001-inverted-priority-assumption.md`.

## Training and environment
- **No PPO training**. Real training steps **0**: strategy-only rule tuning. PPO hyperparameters/model SHA256/checkpoint/optimizer state **not applicable**.
- TavernGym 1.1.0, runtime source fingerprint `6d8712c93022ba11`, pinned source commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, observe2 float 4017/card slots 447/legal actions 245.
- Decision policy: `planned-turn-buy-before-upgrade-v1`. Seat zero controls one player; other seven are real `Game.bot_play` rules bots. Mask validated before step. Game must reach `Game.is_over()`.
- Model roles: Best none for this rule candidate, Candidate research-only, Latest no model artifact.
- Running code: `python -m tavern_ai.upgrade_priority_s_20261102_9c034841 --seed 49101 --eval-seeds 49111 49112 49113 49114 --out outputs/s-20261102-9c034841`.

## Mandatory complete match — candidate itself
- Seed **49101**, full receipt `experiments/s-20261102-9c034841/001-49101.json`.
- **Completed true**, 17 turns, 45 controlled decisions, rank **7**; all eight final placements **[7,8,4,3,2,6,5,1]**.
- No illegal action error, **0** truncated combats, turn-limit-end **false**. This was the candidate rule policy, not a fallback PPO or a claimed PPO model.

## Independent paired evaluation

| Seed | Original baseline | Candidate buy-first | Candidate minus baseline |
|---|---:|---:|---:|
| 49111 | 7 | 8 | +1 |
| 49112 | 8 | 7 | -1 |
| 49113 | 8 | 8 | 0 |
| 49114 | 8 | 6 | -2 |

- **4 complete games per arm, 9 genuine full games total** including the separate mandatory seed.
- Mean placement original **7.75**, candidate **7.25**; paired delta **-0.50**, sample SD **1.291** (lower is better).
- Baseline first-place rate **0%**, candidate **0%**. Both top-four rates **0%**.
- Results are **descriptive only; improvement NOT verified**. Only four seed pairs, almost all placements near the bottom, and trajectories differ despite seeded pairing. No promotion to Best.
- Full report `reports/s-20261102-9c034841/paired-report.json`; candidate receipts `experiments/s-20261102-9c034841/001-*.json` through `005-*.json`, baseline receipts `reports/s-20261102-9c034841/baseline-*.json`; each receipt is actual successful-run console output saved unchanged in its values.

## Evidence durability and continuation
- Original successful run https://github.com/sstxww/reinforcement-learning/actions/runs/41415146112; log job 125177071614; Artifact ID **13126913557**, expires **2026-12-02 08:45:35 UTC**. Compact evidence and research documents are retained in Git.
- No permanent PPO checkpoint was created or represented.
- Session-specific workflow now only triggers on changes to the policy or regression tests, not a report-only push. Bounded runner, dedicated concurrency group, no auto-commit or trigger loop.
- Round 002 hypothesis: instrument how often legal upgrade opportunities are actually displaced by purchases, then correlate that intervention rate and board strength to placements over additional held-out seeds. Do not blindly rerun this n=4 claim.
