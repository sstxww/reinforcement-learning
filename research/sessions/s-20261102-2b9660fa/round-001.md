# s-20261102-2b9660fa — Round 001 · V5 P0/P1 integration-first continuation hardening

## Scope and ownership
- Exclusive repository: `sstxww/reinforcement-learning`; branch `agent/s-20261102-2b9660fa/optimization-001`; base main `1afd8297e3c661bee3117ac5301b1ca08d64869b`.
- An independent session; no changes to other agents' branches, to upstream AutoTavern, or to the ranked Arena.
- Current GitHub review at initiation: 75 open PRs, 74 Draft, only #15 non-draft but stacked on #9; GitHub main CI #41432038040 succeeded on its contemporaneous main head `db5e23ae8c218808821327d806b05d2604cfadfb`. Main continued advancing; recheck before integration.

## P0 actual integration review
- PR #93 had an old passing run but its test asserts exactly four canonical models, whereas latest main has five. The module also duplicates part of already-merged Release validation. We left a concrete blocking review comment at https://github.com/sstxww/reinforcement-learning/pull/93#issuecomment-6577810290 and deliberately did **not** merge it.
- No PR merged by this session; neither a Draft flag nor branch CI was bypassed.
- Re-review current heads and CI/receipts when choosing a future PR to merge.

## P1 source-confirmed defect and narrowly scoped repair
- Main's `train.yml` recovered only a temporary 90-day Action Artifact, swallowed download errors and silently initialized a fresh random model. `train.py` did not validate ZIP/checkpoint hash before loading and did not emit its own checkpoint digest in saved metadata.
- Our candidate adds `tavern_ai/continuation_gate.py`, a fail-closed offline archive preflight reusing main's `checkpoint_preflight`, and `tests/test_continuation_gate_2b9660fa.py`. Missing/partial/legacy-unhashed, tampered, or incompatible archives fail; fresh starts require explicit opt-in. This is an archive gate, **not a proven optimizer-resume or performance check**.
- A proposed main-only workflow amendment supports an explicitly chosen Release tag, verified against the existing two-asset digest index and optionally SB3 CPU load before training. Missing previous Artifacts now abort instead of silently training from scratch.
- `train.py` proposed change checks resume before model load, emits `checkpoint_sha256`, `parent_checkpoint_sha256` and `increment_timesteps`.
- Shared training/workflow changes are **proposed, not merged**; integrate only after independent latest-head CI and review. Existing direct-in-place saved checkpoint atomicity, centralized evaluation uncertainty/seat rotation, automatic verified Release fallback and durable post-training publishing remain open work; don't claim complete P1.

## P2 actual source-backed rank-eight diagnosis
- Main `reports/s-20261102-68099929/003-buy-opportunity.json`: one genuine matched seed 99128, V5 checkpoint SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` had **35 decisions with some BUY legal, 0 BUY chosen**, rank 8; baseline **21 BUY-legal states, 14 chosen**, also rank 8. These are dependent decision-state observations, not 35 independent games.
- Additional independent PR #103 reports three model eight-seat games, 521 BUY-legal decision states and no BUY; three model placements [8,8,8] with guard use. The evidence implicates purchase avoidance/action loops, not a uniquely proven reward or learning-rate cause.
- Main registry latest is **unpromoted** V5 1408-step candidate in Release `v5-s-20261102-68099929-1408-41428692617`; main best/Champion are null. Registry has five candidates. Neither latest model's post-publication optimizer resume nor its competitiveness is certified.

## Training, games, checkpoints and honesty boundary
- This session has run **0 new PPO gradient steps**, produced **0 new model weights**, **0 model-controlled full games**, **0 verified model-strength improvements**, and initiated **0 ranked Arena games** at report creation.
- **Now independently verified:** GitHub Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41450660620 completed **SUCCESS** on source head `c4859e52ea43178b93ce7bc19a7c4dd06756e6a5`; fail-closed continuation regression test step **SUCCESS**, pinned TavernGym 1.1.0 source hash `6d8712c93022ba11`, authentic completed eight-seat baseline seed `85621` controlled seat 0 **place 6**, **18 turns**, **77 decisions**, placements `[6,4,5,8,1,7,3,2]`, zero truncated combats, no turn-limit termination. Receipt `experiments/s-20261102-2b9660fa/001-85621.json` is actually committed at `274ec3e15a60bf08b19e39bc1211fcc49424fb73`; model hash null because it was baseline, not PPO. This test does not establish the proposed model resume or competitive improvement. Latest PR-head CI is independent and must still pass.
- Model weights are not committed in Git. Existing Releases remain source of historical models; no Champion promotion or new durable checkpoint from this session.

## Required next gates
1. Run gate tests against exact latest source and a real independent eight-player TavernGym baseline match; commit genuine receipt under `experiments/s-20261102-2b9660fa/`.
2. Verify latest-head PR CI and source compatibility with concurrently changing main; repair any reproducible regressions.
3. Perform finite Release-backed resume validation and full model-only match before any expansion. Gate training or promotion on objective behavior and paired independent seeds, not on step count.
4. Only after independent review consider selective integration. Never erase another session's data or bypass Draft restrictions.
