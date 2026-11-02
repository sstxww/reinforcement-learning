# V6.1 Round 001 — canonical paired raw-vs-assisted alias integrity

**Session:** s-20261103-5ac92b95 (WORKER). **Task key:** `evaluation/paired-guard-alias-integrity`.
**Initial main:** `3602f64b798bb51dcf69ef5964fe0b4c4cd39495`; own `agent/s-20261103-5ac92b95/optimization-001`; only allowed repository `sstxww/reinforcement-learning`.

## Integrations / claims audited
GitHub REST showed the sole ready PR #15 is stacked on still-unmerged Draft #9, while newly merged #116/#117/#125/#140/#152/#154/#157/#162 already protect Release restore, staged checkpoint writing, paired evidence and receipt rank uniqueness. PRs #161/#164/#165/#167 concern distinct or overlapping release/resume work and are still Draft. **This session merged no PR**. We did not acquire a globally exclusive claim: isolation is by our branch and narrow code path. Any new same-file maintainer change requires rebasing/review.

## Falsifiable P0/P3 failure mode
On initial `main`, `tavern_ai.paired_receipt_gate_v5._guard_count` enumerated singular `guard_forced_end`, but omitted plural `guard_forced_ends` emitted by true raw/guarded behavior audit, and omitted `fallback_actions` checked by `tavern_ai.evaluate`. An otherwise structurally valid `policy=model` receipt with those counters >0 could be accepted as an unassisted candidate. The paired statistics gate must fail closed, not infer a pure model win from an assisted result.

## Implementation and verifiable tests
One minimal production change extends the existing counter list with source-used aliases (including nested diagnostic counters), and rejects an explicitly non-raw `raw_model_only` flag for `policy=model`. New session-namespaced synthetic negative tests cover real aliases, nested counts, boolean values, baseline contamination, compatibility with canonical model receipts and assisted-only classification. These synthetic fixtures **are not games**.

## Own work and limitations
Isolated read-only, one-shot workflow will execute the test and one real pinned-TavernGym **baseline** eight-seat game, uploading the genuine receipt as short-term CI artifact for subsequent GitHub commit. This is infrastructure verification, **not a model strength claim**. Model training increments=0; no new candidate/Release/model hash. The 1408-step existing candidate's previously published heldout rank 8 in three seeds remains a **prior result by other sessions**. No Arena access.

## Exit gate
Own real full-game receipt (8 unique ranks, no truncation) committed under `experiments/s-20261103-5ac92b95/`, exact-head GitHub CI green, integration review of any overlapping edits. Draft until those conditions; no main merge by WORKER. Next distinct hypothesis only if this gate is resolved: whether omission of explicit raw-model-only attestation permits misleading receipt provenance in the canonical canary interface.

## Real result / artifact readback (completed after initial branch commit)
- Read only our own GitHub Actions run [41510322107](https://github.com/sstxww/reinforcement-learning/actions/runs/41510322107), completed **success**; pinned engine, full test suite, genuine full baseline game, exact registered Release SHA, source model load/inference, full raw PPO game, and 1-seed descriptive paired gate all succeeded.
- Downloaded original ZIP Artifact **13173380337** and independently examined both unmodified receipt JSON files. Original run Git SHA `c413543aadab7acf7d9a8a3c1f1177c349291ff7`; receipt bytes SHA256 baseline `f16a107cd915278bdcffdacf5fc6ac4eacb92587d7db5e2be114ae3df0cf2bcc`, model `10f3e316d20bdbf9b79118127aebc5f0cb9d73fd0fb3fe2db42dc5d0317f3988`. Stored under this branch `experiments/s-20261103-5ac92b95/` for durable research source; CI Artifact still ephemeral.
- **Baseline**: seed=99753, seat0 rank=7, placements=[7,2,8,4,1,3,5,6], decisions=39, turns=13; completed=True; truncated_combats=0; turn_limit_end=False.
- **Raw unassisted existing PPO 1408-step model**: same seed/seat, rank=8, placements=[8,6,7,1,3,2,4,5], decisions=121, turns=16; completed=True; truncated_combats=0; turn_limit_end=False; SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.
- Real paired report: n=1, candidate rank 8 vs baseline 7, delta +1 (worse), top4=0, first=0, interval null, promotion_authorized=false. This is additional negative rank-eight evidence, not proof of a singular causal pathology. No new PPO updates, weights, optimizer or GitHub Release were produced.
- Release preflight one-action verified archive integrity/CPU load/engine dimensions; optimizer_resume=not_tested. Original standard-output preserved in `reports/s-20261103-5ac92b95/001-release-preflight.log` (not a standalone JSON document).
- GitHub PR CI initial run [41510410611](https://github.com/sstxww/reinforcement-learning/actions/runs/41510410611) completed 353 passed/1 skipped; **failed only on** `Missing independent agent game receipt` because running own canary was not yet committed. This is a recoverable evidence ordering gate, not a regression failure. Original receipts added in this single commit; verify next PR CI before any Ready/merge status.
