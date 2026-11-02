# V5 integration evidence audit — s-20261102-53ca82c3 / R001

Source: user V5 Gmail TXT instructions, GitHub REST reads on 2026-11-02.
Base main: `31dc7c82ad2fcba461706b4f324d743b5c1c2b9e` (the main branch is being changed concurrently).

## P0 PR triage (at first inventory)

- 64 open PRs, 63 draft; these are a time-bounded snapshot, not a guaranteed current count.
- **A ready for safe merge:** none confirmed by this session. A green historical CI is insufficient.
- **B dependency/conflict:** #8 infrastructure is Draft and `mergeable=false`, touching shared workflows, receipts, registry, README; #9 V1 learning remains Draft; the only non-Draft #15 is based on #9's branch rather than main and explicitly requires #9 first. No blind merge.
- **C more performance evidence:** #73 upgrade gating n=4 paired heldout, #72 sell-swap n=4, #35 opening upgrade delay and many other exploratory results do not establish durable gains.
- **D negative or inconclusive:** #71 blind sell worsened paired rank; #76 20-pair replication mean difference -0.10 with interval spanning zero; #77 selected threshold never intervened on heldout. Preserve the research conclusions but do not promote policy.
- **E overlapping/duplicate proposals:** #67/#68/#75 native card catalogs, #61/#62/#63/#64 BC variants, #51/#60 PPO diagnostics; these need dependency and source review before integration.
- These are examples, not a comprehensive per-PR code review. The separately stored open-PR snapshot includes every returned PR, draft flag, and head SHA. Per-PR current-head CI remains an explicit next review requirement.

## Direct integration extracted from #8

The draft infrastructure PR #8 includes a conservative cleanup utility `scripts/cleanup_temporary.py`. This session independently extracted that self-contained utility into a new minimal PR rather than force merging all 25 files of conflicted #8. Added extra exclusion for `.venv`, `.tox`, `outputs`, `runs`, and 15 regression cases. Does not modify training, model registry, shared CI, baseline, or other sessions' experiments.

Local isolated test command: `python -m pytest -q tests/test_cleanup_temporary.py`; result 15 passed on 2026-11-02. This is only a unit-test result, **not** a real TavernGym match, checkpoint restoration, or competitive improvement.

## P1 checkpoint/storage findings

- The main branch at inspection had no `models/` directory. Draft #8 proposes registry.json, but it is not yet merged or integrity-certified.
- Six GitHub Releases were present with model.zip assets. Latest clearly described V2 candidate is `v2-learning-41413557445`: 17,525,115-byte asset SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- Release metadata and availability alone **do not** certify local download, load, optimizer-state continuation, inference, or model promotion.
- Other active V5 sessions are creating checkpoint preflight and model registry tools; this session did not modify those overlapping paths. Do not expand PPO training until that work is validated.

## P2 why rank 8? Source-grounded leads, NOT established universal root cause

- #9 reports a 256-step PPO candidate ranked [8,8,8] on three heldout games. #15 reports continued 1280-step candidate ranked [8,8,8,8] on four heldout seeds, whereas same-seed rules baseline ranked [7,6,8,8].
- #60 reports a low learning-rate checkpoint chose 0 BUY actions across three complete heldout games, with 21 END_TURN actions out of 36 model-selected actions. Distinguish a true declined legal-buy opportunity from inability to afford or buy: count `mask[8:16].any()` and gold/board/hand state per decision.
- #24 reported a compact extractor also placed eighth despite completing full model-controlled game; changing architecture size alone is not proof of strength gain.
- Immediate falsifiable diagnosis: for each legal BUY opportunity, record ability to buy, selected action type, gold and remaining board slots; compare ending-turn choice with identical public observation and legal mask. Audit action encoding, reward/observation normalization and effective model decisions before training more.
- None of these records supports a definitive single cause of repeated rank eight, nor a claim that a stronger Champion exists.

## Merge and training gates

Do not merge #8/#9/#15 without latest-head CI, upstream-dependency audit, complete real-game evidence and main health. Do not promote any Release as Champion or launch large-scale PPO until independently reproducible checkpoint restoration and heldout model gameplay are verified. Formal ranked TavernArena prohibited without additional authorization.
