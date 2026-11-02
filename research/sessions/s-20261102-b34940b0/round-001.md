# Round 001 — last-vs-first generic forced-choice action (negative result)

## Identity, code provenance and hypothesis

- Session: `s-20261102-b34940b0`, branch `agent/s-20261102-b34940b0/optimization-001`, draft [PR #32](https://github.com/sstxww/reinforcement-learning/pull/32).
- Based on main commit `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`; code commit `adf99fc8c229f366c8790a904f970643229d7381`; genuine evidence commit `51a1ed3212670e18e852327bf774f1678301d4ec`.
- Hypothesis: swapping the first legal option for the last legal option within compulsory action IDs 30–45 improves seat-0 final rank versus original `BaselinePolicy`.
- Motivation: main baseline always chooses the first legal `Choose`; other draft PRs already cover PPO rewards/embeddings, buying, selling, refresh, upgrade and board placement. No common policy files or model weights were modified.
- Crucial scope correction from reading upstream `crates/taverngym/src/actions.rs`: 30–45 is the generic `Choose` range. It includes **hero selection**, Discover, Choose One, pending targets and trinket offers. Thus this test is *not a Discover-only experiment*. The source's legacy variable name `multi_option_discover_choices` actually denotes all generic multi-option choices, and should not be interpreted as a Discover-only counter.

## Actual engineering experiment

- [GitHub Actions run #41415645714](https://github.com/sstxww/reinforcement-learning/actions/runs/41415645714), **success**, all jobs/steps successful, 11 unit tests passed before engine install.
- TavernGym **1.1.0**, source hash `6d8712c93022ba11`, observe2 4017 features/447 card indices/245 legal-masked actions.
- Four fresh independent paired seeds 65201–65204, baseline and altered rule candidate control one player seat against seven official rule bots, eight complete `Game.is_over()` games. The actual simulation rejects illegal policy actions and validates receipts. No combat truncation or turn-limit ending.
- Rule ablation: **0 PPO gradient/optimization steps** and no neural checkpoint; there is no training configuration other than the deterministic policy and four seeds.
- Candidate strategy file `tavern_ai/discover_slot_ablation_s_b34940b0.py`, SHA256 `bdfba87d599e31e458b575e8156fe8497b5b7724a2d788b42af9f1dc2d6af773`; original baseline module SHA256 `e4722a44660f8a880c9eeb949c80e81ebb652926f43d71acd64f958762bd6bac`.
- Model weights SHA256: **N/A**, no model trained. Model checkpoint: **N/A**. Git blob/commit pins the rule candidate source for reproducibility.

## Real game results

| Seed | Baseline rank | Candidate rank | Candidate own decisions | Candidate final eight ranks |
| --- | ---: | ---: | ---: | --- |
| 65201 | 4 | 8 | 39 | [8,6,4,5,2,1,7,3] |
| 65202 | 8 | 8 | 38 | [8,2,4,5,1,6,7,3] |
| 65203 | 6 | 8 | 33 | [8,4,1,2,3,6,5,7] |
| 65204 | 5 | 8 | 49 | [8,1,5,3,7,6,4,2] |

Baseline mean rank **5.75**, first 0%, top4 **25%**. Candidate mean rank **8.00**, first 0%, top4 **0%**. Paired candidate-baseline rank differences `[4,0,2,3]`, mean **+2.25 ranks (worse)**. Candidate encountered **21** multi-option generic `Choose` decisions. Exact source metrics at `research/sessions/s-20261102-b34940b0/metrics-001.json`. Eight independently generated receipts at `experiments/s-20261102-b34940b0/001-<seed>.json` and `experiments/s-20261102-b34940b0/controls/001-<seed>.json`.

## Interpretation and quality gate

All four candidate games completed with legal actions, so the safety and engineering gate passed. The selected change showed **no improvement** and a large negative descriptive effect against the original rule in this seed sample. However n=4 is too small for any confident general game-strength claim; selection includes hero choice and other pending interactions, making causal attribution to Discover **invalid**. Do not integrate candidate into common baseline, replace Best, or claim Arena strength.

The successful Actions run persisted JSON through commit `51a1ed3...`; runtime Artifact retention is 30 days but persistent source/metrics/receipts live in Git. No repo cleanup or unrelated file deletion was performed. No simulator, credential or official Arena matches were modified.

## Operational learning and next hypothesis

- The upstream action map is necessary to interpret a mask-only strategy intervention. Wide action index ranges may encode heterogeneous game decisions even if all are labelled `Choose`.
- A silent generic slot bias can radically change results while preserving legality; legality does not imply strategy quality.
- Next round should isolate opening hero selection from other pending choices, and then evaluate separately on new held-out seeds. Do not repeat last-slot global bias as a purported improvement.
