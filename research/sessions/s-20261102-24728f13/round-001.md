# s-20261102-24728f13 · Round 001: masked PPO learning-rate sensitivity

## Hypothesis and context
Reducing the learning rate from 3e-4 to 1e-4 with all other training settings and the seed fixed might improve short-budget MaskablePPO progression and heldout placement. This was chosen after checking main and open PRs to avoid overlapping other Agents' reward-shaping, entropy, architecture, position, purchase and guard investigations.

- Independent session: `s-20261102-24728f13`; branch: `agent/s-20261102-24728f13/optimization-001`
- Base main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Review PR: https://github.com/sstxww/reinforcement-learning/pull/51
- Historical lessons: main `research/knowledge/INCIDENTS-20261102.md`, PR #9 (candidate PPO full-game guard issue), PR #15 (1,280-step resume with no rank gain), and isolated PR #20 (entropy study). These are context, not this session's results.
- Only session-owned files added; no changes to main shared modules/workflow, other branches, other Agent files, AutoTavern upstream or Arena.

## Exact engine / experiment configuration
- Real TavernGym `1.1.0`, source fingerprint `6d8712c93022ba11`; pinned upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`; observe2 patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Engine runtime contract: float features 4017, card slots 447, discrete legal-masked actions 245.
- Same training seed `24728` for both arms; MaskablePPO, MultiInputPolicy, TavernExtractor, n_steps=128, batch_size=64, n_epochs=4, gamma=0.99, gae_lambda=0.95, ent_coef=0.01, CPU.
- Reference learning rate: 3e-4; candidate learning rate: 1e-4; actual executed: 256 steps per arm, **512 total**.
- Masked deterministic model inference; a legal END_TURN override is allowed after 40 actions in a turn, counted per receipt. This is a **guarded model policy**, not wholly unconstrained inference.
- Independent heldout seeds: `42171, 42172, 42173`, three games per arm. Each game uses one model-controlled seat against seven genuine TavernGym scripted bots.

## Actual execution and evidence
Training and six complete eight-seat matches: https://github.com/sstxww/reinforcement-learning/actions/runs/41416467100 (all steps success).
Model restoration from that run's Artifact: https://github.com/sstxww/reinforcement-learning/actions/runs/41417110915 (all steps success).

The model training script is `tavern_ai/lr_probe_24728f13.py`, with targeted `tests/test_lr_probe_24728f13.py` (passed). Own workflows `experiment-s-20261102-24728f13.yml` and `recover-s-20261102-24728f13.yml` are bounded and isolated.

| Arm | Seeds | Seat 0 placement | Mean | Top 4 | First | Decisions | Forced END_TURN |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| reference 3e-4 | 42171–42173 | [8,8,8] | 8.00 | 0/3 | 0/3 | 759 | 18 |
| candidate 1e-4 | 42171–42173 | [8,8,8] | 8.00 | 0/3 | 0/3 | 66 | 0 |

All six real receipts have `completed=true`, exactly eight placements, zero illegal actions, zero truncated combats, and `turn_limit_end=false`. Seed-specific candidate decision counts: 30, 24, 12. Reference: 290, 214, 255. Example mandatory candidate receipt `experiments/s-20261102-24728f13/001-42171.json`; the five others are in the same directory.

Compact per-seed analysis: `reports/s-20261102-24728f13/001-lr-ablation.json`; exact restore-check: `reports/s-20261102-24728f13/001-checkpoint-recovery.json`. No output in these files was fabricated or estimated.

## Checkpoints / restoreability
- Candidate SHA256: `802c65e7da2ba42e26e2f2efb55859b91428f1b792428031947484ce95f42f18`.
- Reference SHA256: `8450905bdd1d78e6be68175f9943b16ac840fc9ce2882da4e32791ddb078ad0c`.
- Temporary Artifact: `lr-study-s-20261102-24728f13-41416467100`, ID `13128665279`; created Nov 2, 2026 and expires **2026-12-02 08:58 UTC**. Archive integrity digest: `sha256:e49594180456a76a0b60062d47186ce680a807de8c887c423107816d2751683d`.
- Restore validation re-downloaded both checkpoint files, matched the above SHA256s, loaded each using CPU MaskablePPO, verified `num_timesteps=256` and predicted a legal masked action on the actual TavernGym observation. Reference action 31, candidate action 30 in this smoke test.
- No permanent backend or unexpired-offsite backup was set up. Neither checkpoint is Best; both are exploratory candidates. Temporary output/caches are not committed.

## Outcome, risks, next study
**No detectable placement improvement** with the lower learning rate in this tiny trial; both policies were last in all three paired games. The 66 vs 759 action-count difference is not evidence of better play and may indicate premature end turns / lack of economy actions. n=3 per arm is insufficient to establish general superiority or equivalence.

No new failures were observed in either completed dedicated workflow. The historic Model loop and Release 403 incidents were not reproduced here and should not be described as globally fixed by this work. No Arena ranked game was entered.

Next test hypothesis: quantify meaningful buying/playing/upgrade decisions and premature END_TURN frequency from real heldout trajectories, rather than more microlearning-rate sweeps. Use an isolated telemetry runner and several heldout seeds, without changing shared trainer or assuming more actions means higher rank. Latest PR CI must be checked against the final head commit before review completion.
