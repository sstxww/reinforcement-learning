# s-20261103-bf44b161 round-002 — production manual Release custody fallback

## Integration origin
Current main at round start `e837e7b445cfb74a84fdb871a4bae4ec9e0ce034`. While R001 ran, others safely merged #117 (manual-only registered Release restoration) and #125 (SHA-bound checkpoint writer), superseding R001 patch; R001 PR #160 was closed unmerged after genuine isolated proof. R001 Action #41508263674 succeeded 7 new tests, 308 total passed, 1 skipped; authentic baseline seed 98631 rank2, 14 turns, 62 decisions, 0 truncations; receipt is kept in R001 branch. This is not model ability.

## Verified new main risk
`.github/workflows/train.yml` already downloads and verifies registered Release and stores a successful candidate as a new immutable unpromoted Release. But if the `gh release create` step returns 403 or another publishing failure, `if: always()` Artifact only included `artifacts/*.json` and `checkpoints/candidate.metadata.json`, **not the 17 MB candidate.zip weights**. Without published Release and with ZIP omitted from Artifact, real newly trained checkpoint bytes would be lost. Earlier #121 explicitly observed Release HTTP 403 despite `contents:write` on its separate workflow. This is a real source-level storage safety failure mode, not proof main's Release publisher has failed in production.

## Minimal code
- Preserve existing manual registered-source PPO workflow, source SHA+CPU+ZIP check, model-only full-match, paired eval and no Champion promotion.
- Before Release publish, write a SHA256 checksum receipt for the two candidate files.
- On `always()` upload candidate ZIP, metadata, checksum and game/evaluation reports with an isolated `run_id/run_attempt` artifact name and 90-day retention. This is emergency custody **only**, never permanent storage.
- Add `tests/test_train_custody_fallback_bf44b161.py` static workflow invariant checks. No token permission increase beyond already merged main.

## Real bounded proof, do not preclaim
- Isolated one-shot workflow `.github/workflows/v5-custody-s-20261103-bf44b161-r002.yml`, push trigger only under this session's `run-trigger-002.txt`, timeout 105 min.
- Run full unit suite and pinned engine.
- Own genuine baseline eight-player match on seed 98632, commit receipt `experiments/s-20261103-bf44b161/002-98632-baseline.json` only after completion.
- Load actual registered unpromoted 1408-step Release and attempt **exactly 128 real PPO continuation steps** into separate `checkpoints/candidate.zip`, verify parent/new SHA+step metadata, attempt raw model game seed 98633 and two paired heldout games seeds 98634..98635.
- Whether model game passes or fails, `if:always` archives the candidate ZIP and SHA if actually generated. No Release publication by this isolated proof, no fake Champion. The isolated Artifact expires in 90 days.
- Distinguish PASS/FAIL in actual Actions logs. No result claimed before running. If raw candidate does not finish, mark candidate rejected and retain evidence; never call fallback rank a raw model result.

## Rank-eight research context
Main registered latest unpromoted 1408-step model has SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, heldout [8,8,8] vs baseline [6,8,8]. Main seed 99128 evidence: 35 BUY-legal states / 0 purchases / 37 refresh / 70 other actions, rank8; baseline had 14 BUY in 21 legal states but also rank8. Draft #107 forced 46 buys without improving rank. Likely economic/action-selection pathology, not a confirmed single causal root. No hyperparameter expansion based on small samples.

## Integration acceptance
Keep Draft until latest-head CI real-game receipt, code review and up-to-date main diff. Never overwrite another agent branch or force a losing model into Champion. Record exact Action and Artifact URLs/hashes after run.


## R002 executed result — 2026-11-03 (+08:00)
- Own [Actions #41509203645](https://github.com/sstxww/reinforcement-learning/actions/runs/41509203645): **3 new custody tests passed; 328 total passed, 1 skipped**. Pinned TavernGym 1.1.0 installed; genuine own baseline seed **98632** completed, rank **7**, 15 turns, 43 decisions, placements `[7,8,3,1,5,6,2,4]`, zero truncations. [Actual JSON receipt](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261103-bf44b161/optimization-002/experiments/s-20261103-bf44b161/002-98632-baseline.json).
- True verified registered Release checkpoint continuation **1408→1536** (+128) finished. Parent SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; child SHA256 `ce1e1f35841eb4239f854ebc2706505af126d7a820cf589cadb93a79502a735b`.
- Candidate **FAILED** real unguarded model-only full eight-seat seed **98633**: `RuntimeError: Full-game safety limit exceeded`. No completed match, ranking, win/top4 percentage or raw match receipt; the two planned heldout games were **skipped**. Model is **REJECTED_UNPROMOTED**. Failure report `research/sessions/s-20261103-bf44b161/failures/002-raw-model-safety-limit.md`. This run did not prove a causal action loop family.
- The failed model ZIP, metadata and checksums were in a [90-day Artifact 13172197990](https://github.com/sstxww/reinforcement-learning/actions/runs/41509203645/artifacts/13172197990), expiry 2027-01-31.
- A separate **one-shot** [Release publication run 41510224472](https://github.com/sstxww/reinforcement-learning/actions/runs/41510224472) succeeded: re-downloaded Artifact, SHA-verified bytes/optimizer/metadata and parent lineage, published [REJECTED 1536-step prerelease](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-rejected-s-20261103-bf44b161-1536-41509203645), re-downloaded `model.zip` and `model.metadata.json`, compared bytes equal. Release contains `model.zip` (17,525,202 bytes), `model.metadata.json`, `checksums.sha256`, `rejection.json`. **No Champion/Best update.**
- Both one-shot workflows are session-only test infrastructure. Clean up these workflows and trigger files from integration PR #166 after preserving run URLs and evidence. Production change is only main's emergency candidate ZIP+SHA fallback with 90-day retention.
- Integration readiness: await **latest final head** full-match CI, current-main diff and review before converting Draft; no bulk PPO training or Arena.
