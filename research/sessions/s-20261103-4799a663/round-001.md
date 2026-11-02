# s-20261103-4799a663 R001 — own genuine paired raw model probe

## Hypothesis and isolated implementation
A new independent same-seed game may reproduce raw 1408-step model failure or rank eight while a baseline is playable. This tests completion/rank attribution but does NOT establish causal no-BUY or model improvement. Use a fixed, independent seed 99687, controlled seat 0 and exactly seven TavernGym scripted bots. No guard/fallback; do not silently convert incomplete model games to eighth place.

- Code: `scripts/v7_raw_pair_s_20261103_4799a663.py` verifies model sha against canonical registry before inference, uses existing `tavern_ai.canary.run` unchanged, requires unassisted complete eight-seat permutation, creates an explicit failure JSON with rank null for exceptions, and always attempts independent baseline game.
- Tests: `tests/test_v7_raw_pair_s_20261103_4799a663.py` synthetic valid, falsified, incomplete, assisted, identity cases; not game receipts.
- Live workflow: own branch only, read-only GITHUB_TOKEN, bounded 45 min, unique concurrency, pinned engine and official Release recovery; artifact retention temporary 30d, no model publication.
- No code touched in shared `train.yml`, `tavern_ai/train.py`, registry, existing PR branches, or upstream repository.

## Integration-first decisions
Main @ `c1b828734527bae6141805581693d890cc3bff94` has integrated #165 privilege split, and real postmerge CI #41512315964 passed checked eight-player job steps. New main changes require fresh CI audit. #175 release restore no-clobber PR has exact-head CI #41511418837 success; it is non-Draft, but currently lacks a safe exclusive main merge lease and needs latest main base compatibility + independent review. #184/#185 already cover serialized integration gateways; do not duplicate them or infer global lock from one branch.

## Data custody and limits
Official source 1408-step model SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` and metadata `51a651c3a1921447e7bc06c301a52e85331411e75d61b35b5330c43a55aeba9c`. Independent Release download/inference run pending. PPO additional steps 0; no new checkpoint, optimizer, Release or Best/Champion.
Raw game status, baseline status, same-seed rank, actual seed/receipt and sample uncertainty remain pending; no evidence invented.

## Failure/next-round contract
A model stall, 30k-action cap, mismatched model hash, malformed permutation or simulator error must generate a `*-failure.json` and `rank: null`, never a completed receipt. Preserve exact SHA/job URL, investigate public-state action loops before retraining. After real completion, commit untouched authentic receipts from log/artifact to `experiments/s-20261103-4799a663/` and only then update PR readiness. Never interpret a single seed as a strength result.

## Verified R001 live results (read back from original GitHub Actions)
- Bounded, unique original [workflow run 41513448828](https://github.com/sstxww/reinforcement-learning/actions/runs/41513448828) **SUCCESS**; actual job `125510847500` successful: 11/11 own synthetic tests; GitHub-pinned native TavernGym 1.1.0 contract; registered immutable Release download and model CPU load; actual model and baseline complete-game attempts; original Artifacts upload.
- Original [artifact 13175291485](https://github.com/sstxww/reinforcement-learning/actions/runs/41513448828/artifacts/13175291485) ZIP SHA256 `f28332a6bbc6776de26bd137c7c599b32b0a3322d2f112458168de7067e16349`, size 1456 bytes, retention 30d, NOT permanent model storage.
- From original Artifact ZIP three files were committed byte-for-byte unchanged under `experiments/s-20261103-4799a663/`, then read back from GitHub and verified by matching exact Git blob SHA1:
  - `001-99687-model.json`, original SHA256 `e1047e3a2a4b39a64089de45f37388367b2c7867b1309bf02a552422e433d55a`, Git blob `e11fddcb03cede8e2f9a8816a5dfa3babde2a57c`. **Raw deterministic PPO** seed99687 seat0 rank **8**, placements `[8,3,2,1,7,5,4,6]`, 14 turns, 122 decisions, `completed=true`, `truncated_combats=0`, `turn_limit_end=false`, no rescue.
  - `001-99687-baseline.json`, original SHA256 `ab38b05e67e5f092c1b5c7c333bdd1ab9e1fbcd93745c3ab6a2186fadf42f1d4`, Git blob `3e2967063ff5fcdd8adcfb9269b320d9687eeb4f`. **Script baseline** same seed/seat/rules rank **8**, placements `[8,4,3,7,5,2,1,6]`, 13 turns, 43 decisions, complete, zero truncation.
  - `001-99687-status.json`, original SHA256 `6fe0ca5fd0ca8b8c841ae9240e5be11f16a44a819959ca959fb24f5d7ebf3cd9`, Git blob `635860e24cd67cf01b62930a9aaad032601572c9`: same-seed raw model minus baseline placement delta **0**, n=1, not a strength conclusion.
- Release restore returned `cpu_load_verified=true`, `weights_and_metadata_hash_verified=true`, source model weights SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` and metadata SHA256 `51a651c3a1921447e7bc06c301a52e85331411e75d61b35b5330c43a55aeba9c`; runner independently printed matching `sha256sum`. **No optimizer continuation performed here**; existing saved source Release is not our own new candidate.
- Results indicate 1408-step PPO again finishes only eighth, with 122 decisions vs baseline 43; the difference in action counts is descriptive and does not prove actual no-progress loops or explain causal mechanism without action-level public-state tracing.
- Own new PPO steps **0**; new model Release **0**; new checkpoint **0**; Best/Champion remains **unpromoted**; ranked TavernArena **0**; merged PR by this session **0**.
- PR [#214](https://github.com/sstxww/reinforcement-learning/pull/214) remains Draft until this real-receipt commit's latest exact-head full-match PR CI completes, independent review and genuine serial integrator are available. Do not mistake original branch run for PR exact-head CI.
- Next round: trace raw action categories and public-state before/after hashes / affordable BUY masks on another fixed independent seed, or have the serial integrator review/reuse existing action-telemetry PR #180/#183, before wasting PPO budget. No strength promotion on these results.
