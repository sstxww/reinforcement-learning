# R001 — V7 registered raw PPO vs baseline (new paired seed 99541)

## Scope / hypothesis

Prior real V5 1408-step Release `a73d24c...db2632` has independently completed raw rank-eight games; in historical paired seed 99385 it scored 8 versus baseline 7, and many earlier traces showed no BUY despite legal BUY masks. The causal root is **unknown**. A new raw complete-game sample versus same-seed baseline can extend descriptive evidence, but **n=1 cannot imply generalization or improvement**.

## Protocol

- Pull exact immutable registered `model.zip` and `model.metadata.json` from V5 1408-step Release, validate expected model SHA256 before model inference.
- Use pinned TavernGym 1.1.0 / engine hash `6d8712c93022ba11`, seat 0, seven scripted bots, seed 99541.
- Execute an independently verified baseline full game; execute completely raw deterministic PPO with no forced end, buy assistance, human decisions, substitution or fallback.
- Real full game only when `Game.is_over()`; aborted game gets a separate failure record without rank. Source engine contract 4017 floats, 447 cards, 245 masked actions.
- For two successfully completed authentic receipts, execute the existing `paired_receipt_gate_v5.compare` (n=1 descriptive, not statistically powered) and preserve original files and summary as temporary Actions artifact, then commit verified records.
- Timeout <=35 minutes, read-only GitHub job token, unique concurrency group, one execution per branch path, no workflow self-push. Do **not** consume extra PPO training or publish/promote models on a known rank-eight candidate without first verifying raw behavior.

## Existing evidence / independent P0 review

Existing [PR #168](https://github.com/sstxww/reinforcement-learning/pull/168) documents actual seed 99385 raw model rank 8, baseline rank 7. This is an external source, not this round's own run. Independently verified [PR #185 latest CI](https://github.com/sstxww/reinforcement-learning/actions/runs/41512690022) failed due to missing original own game receipt; posted [review](https://github.com/sstxww/reinforcement-learning/pull/185#pullrequestreview-5742385698) on potential stale CI rerun gate. No merges, no tests or games falsely claimed.

## Expected next work

Read run job/logs and archive original Action artifacts, record exact HEAD SHA, seed, model SHA, completed/aborted separately; if raw fails, preserve error with budget/timeout and do not label it eighth. Check whether current exact main SHA and CI changed and leave an integrator-ready note. Evaluate BUY-opportunity state traces as the next isolated hypothesis only if this seed provides actionable new signal.


## Verified real execution and archiving

- [Actual successful Actions run #41513501276](https://github.com/sstxww/reinforcement-learning/actions/runs/41513501276), job `125511026704`, original experiment SHA `d4c3d7f6dab880e275c2195879713444f500c93b`; original ZIP Artifact `13174107805` (30 days, not durable model storage).
- Independent baseline *real full eight-seat game*: seed 99541, seat 0, rank 8, placements `[8,2,4,6,5,7,1,3]`, 14 turns / 38 actions; file `experiments/s-20261103-ff75e61a/001-99541-baseline.json`, verified original SHA256 `ca63ecd3a223c11f4c8acdeba3665499bc38ab30518abe5c15049d56e8b4092e`.
- Existing immutable 1408-step raw MaskablePPO Release successfully downloaded; `checkpoints/model.zip: OK` for expected SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, then **unassisted** model-controlled complete match: seed 99541, seat 0, rank 8, placements `[8,2,6,1,7,5,3,4]`, 15 turns / 123 decisions; no guard or fallback, `truncated_combats=0`, `turn_limit_end=false`; original file `experiments/s-20261103-ff75e61a/001-99541-raw-model.json`, SHA256 `dc6894052e31aa004c231f47ea7774822e83ccac644ea435d7dfb019b983250a`.
- Canonical paired gate accepted full original data: 1 same-seed pair, candidate minus baseline mean placement 0, top4 both 0, no confidence interval for n=1, no promotion. `reports/s-20261103-ff75e61a/001-99541-paired.json` SHA256 `fd8113104efb0a46bc2224613cfc45240f7af85aa7beac152c1275f48732d401`.
- All 3 files were committed byte-for-byte identical to original ZIP; Git blob hashes matched locally computed original blobs. These are genuine receipts, not synthetic mutation tests.
- Engine source hash `6d8712c93022ba11`, TavernGym 1.1.0 / observe2 and 245 actions; original model has 1408 historic steps, **new steps this round = 0**, 0 Release publication or optimizer save, unchanged Best/Champion.
- Cost boundary: one baseline + one raw model real-game match, no model optimization; running many more uninstrumented rank-8 matches or PPO step increases is unjustified without testing action-loop/economy hypotheses. No rank-gain conclusion. Valid 8-seat simulator completion is not ranked Arena MMR.
- P0 independent review: external PR #185 current original CI [41512690022](https://github.com/sstxww/reinforcement-learning/actions/runs/41512690022) failed on missing independent receipt before full-match step, followed by own review noting stale-created-run recheck risk; no safe main lease obtained and no merges.
- **Next round:** inspect PR exact latest head CI (including an independent simulator game), then pursue a separate minimal P2 raw action-state BUY/END_TURN opportunity probe with pre/post observable hashes and no assisted fallback, instead of assuming too few steps caused rank-eight.
