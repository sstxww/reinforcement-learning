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
