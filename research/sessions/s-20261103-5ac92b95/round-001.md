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
