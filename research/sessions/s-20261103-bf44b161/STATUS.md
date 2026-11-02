# s-20261103-bf44b161 — current STATUS

- R001 original safety proposal #160 **closed unmerged as superseded** by main's #117/#125; original independent proof preserved at [Action #41508263674](https://github.com/sstxww/reinforcement-learning/actions/runs/41508263674).
- R002 branch: `agent/s-20261103-bf44b161/optimization-002`, starts `main@e837e7b445cfb74a84fdb871a4bae4ec9e0ce034`.
- R002 objective: protect candidate model ZIP + SHA if production GitHub Release publish fails; no claim of durable Release.
- R002 proposed files: `.github/workflows/train.yml`, `tests/test_train_custody_fallback_bf44b161.py`, own isolated one-shot smoke workflow, unique session research paths and genuine game receipts if produced.
- R002 Actions state before triggering: NOT RUN. Real PPO steps on this branch thus far **0**; no new model published.
- Baseline seed 98632, raw model seed 98633, paired seed 98634 onward are reserved for this one bounded experiment; no Arena/ranked matches.
- Existing experimental 1408-step Release is the registered source; Best/Champion remain null. No bypass of weights/optimizer/engine SHA checks.
- A 90-day Artifact is emergency recoverability, not permanent model archival. An owner-approved Release publisher and verified re-download remain needed for long-term custody.
- Next: inspect GitHub Actions run, full receipt + result, metadata and Artifact upload. If any gate fails, log exact blocker and stop unsupported model claims.


## R002 executed result — 2026-11-03 (+08:00)
- Own [Actions #41509203645](https://github.com/sstxww/reinforcement-learning/actions/runs/41509203645): **3 new custody tests passed; 328 total passed, 1 skipped**. Pinned TavernGym 1.1.0 installed; genuine own baseline seed **98632** completed, rank **7**, 15 turns, 43 decisions, placements `[7,8,3,1,5,6,2,4]`, zero truncations. [Actual JSON receipt](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261103-bf44b161/optimization-002/experiments/s-20261103-bf44b161/002-98632-baseline.json).
- True verified registered Release checkpoint continuation **1408→1536** (+128) finished. Parent SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; child SHA256 `ce1e1f35841eb4239f854ebc2706505af126d7a820cf589cadb93a79502a735b`.
- Candidate **FAILED** real unguarded model-only full eight-seat seed **98633**: `RuntimeError: Full-game safety limit exceeded`. No completed match, ranking, win/top4 percentage or raw match receipt; the two planned heldout games were **skipped**. Model is **REJECTED_UNPROMOTED**. Failure report `research/sessions/s-20261103-bf44b161/failures/002-raw-model-safety-limit.md`. This run did not prove a causal action loop family.
- The failed model ZIP, metadata and checksums were in a [90-day Artifact 13172197990](https://github.com/sstxww/reinforcement-learning/actions/runs/41509203645/artifacts/13172197990), expiry 2027-01-31.
- A separate **one-shot** [Release publication run 41510224472](https://github.com/sstxww/reinforcement-learning/actions/runs/41510224472) succeeded: re-downloaded Artifact, SHA-verified bytes/optimizer/metadata and parent lineage, published [REJECTED 1536-step prerelease](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-rejected-s-20261103-bf44b161-1536-41509203645), re-downloaded `model.zip` and `model.metadata.json`, compared bytes equal. Release contains `model.zip` (17,525,202 bytes), `model.metadata.json`, `checksums.sha256`, `rejection.json`. **No Champion/Best update.**
- Both one-shot workflows are session-only test infrastructure. Clean up these workflows and trigger files from integration PR #166 after preserving run URLs and evidence. Production change is only main's emergency candidate ZIP+SHA fallback with 90-day retention.
- Integration readiness: await **latest final head** full-match CI, current-main diff and review before converting Draft; no bulk PPO training or Arena.
