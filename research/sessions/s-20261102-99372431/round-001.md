# AutoTavern-AI V5 — s-20261102-99372431 / round 001

## Objective and isolation

- Role: independent P0/P1 integration and safety agent, not an extra subagent.
- Working repository (only write target): `sstxww/reinforcement-learning`.
- Branch: `agent/s-20261102-99372431/optimization-001`, created from main `1afd8297e3c661bee3117ac5301b1ca08d64869b`. Main is concurrently changing.
- No upstream TavernGym changes, no ranked Arena access, no changes to another session's branch or model; no direct push to main.
- Read current README, AGENTS, PROJECT_BACKGROUND, SESSION_PROTOCOL, CLOSED_LOOP, the canonical model registry, shared code, and original V5 Gmail TXT (27,248 bytes).

## P0: existing PR integration audit

First snapshot: 75 open PRs / 74 Draft; later rescan: 81 open / 80 Draft. The only non-Draft is #15, which is based on `agent/learning/v1`, NOT main; parent #9 is still Draft. #15's V2 checkpoint, though persistent, is an unpromoted negative result: held-out ranks [8,8,8,8]. Do not merge it standalone or retarget without resolving the #9 dependency. #9 and the main trainer overlap in checkpoint/provenance logic; wholesale merge risks regressing existing integrated safeguards. Other Drafts explicitly preserve dependency/author gate; no safe unclaimed immediate merge was demonstrated in this pass. No PR merged by this session.

Relevant existing/ongoing work: #79 recovery/preflight has already reached main; #87 model registry extraction reached main; #90 legal-buy diagnostic merged; #103 and #107 are additional still-Draft behavioral studies with overlap. Do not import those wholesale. Historical main CI was successful at `db5e23ae8c218808821327d806b05d2604cfadfb`; later concurrent main heads need a fresh post-merge CI check.

## P1: concrete defect and isolated implementation

Confirmed main code `tavern_ai/train.py` accepts a resume source by comparing only `prev["engine"]` and writes weaker schema-1 metadata; historical real V2 1280→1408 continuation downgraded schema-2 compatibility provenance. The shared `train.yml` currently restores an expiring Actions Artifact rather than an immutable Release. Prior published model Releases alone do not certify safe future resumes.

This branch adds:
- `scripts/verified_resume_s_20261102_99372431.py`: read canonical registry latest unpromoted Release, externally trusted SHA256/ZIP/optimizer/contract preflight, exact 128-step training gate, no source overwrite, cross-check cumulative steps and engine, preserve schema-2 catalog/ruleset/patch/upstream compatibility + immutable source lineage, independently re-preflight output. Produces a machine-readable report with promotion explicitly false.
- `tests/test_verified_resume_s_20261102_99372431.py`: synthetic archive/metadata regression tests only, rejection on mismatched SHA, wrong steps/engine/algorithm, unbounded budget and source overwrite. The synthetic fixtures are NOT model-match evidence.
- `.github/workflows/v5-verified-resume-s-20261102-99372431.yml`: branch-isolated finite workflow. Installs exact pinned TavernGym, first validates its own full eight-player baseline receipt, downloads the registry's Release assets, validates hashes and real CPU masked inference, performs *at most 128* real continuation steps, checks restored schema-2 metadata, attempts candidate-controlled full eight-seat game without hiding failure, and if resume succeeded publishes a labelled **unpromoted** Release with checksums and audit. All experimental evidence lives under this session's own paths. Candidate-game failure is an explicit failing gate.
- Workflow run: https://github.com/sstxww/reinforcement-learning/actions/runs/41449843877 (triggered by workflow push; at initial review it was in_progress). Final status, training steps, real match and Release must be read from actual run, not assumed.

## Model and P2: distinguish established evidence from hypotheses

Canonical registry latest at branch base: `v5-s-20261102-68099929-1408-41428692617`, 1,408 recorded steps, trusted SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; a published Release exists. Held-out candidate ranks [8,8,8] vs baseline [6,8,8] on same 3 seeds. Both `best` and `champion` remain null. This session has not promoted or overwritten it.

Concrete reported historical diagnosis:
- #103, actual three paired held-out full games using *guarded* V2: model had 521 decisions with a legal BUY but chose BUY 0 times, placement [8,8,8], 12 forced end-turn interventions. Absence of BUY is **not** from BUY mask always being illegal in those observed states.
- #107, three more paired seeds: an explicit legal-buy intervention produced 46 real purchases but all three placements remained eighth, with many PLAY/CANCEL cycles and higher end-turn-guard usage. Buying alone is not enough.
- #60 shows low-LR policy END_TURN-heavy and 0 buys, but no causal learning-rate conclusion.
- These experiments are small, sometimes fallback-guarded, and do NOT prove an optimizer/reward root cause, exact strength effect, or that raw PPO can complete unaided.

Next falsifiable question: instrument state-transition-changing PLAY/CANCEL/CHOOSE/Refresh/Freeze action sequences in *raw* model decisions, counting opportunities and mandatory options separately, and compare with a held-out baseline. Never claim a full model match if the guard stops it.

## Verification, training and disposition

- New source was actually committed to the independent GitHub branch.
- GitHub Action run #41449843877 has been triggered. At the time of writing this note, its final CI/training/game outcome was **not yet verified**.
- **New training steps verified in this session so far: 0**. Do not infer 128 from having authored a workflow.
- **New completed own games verified so far: 0**. No made-up receipt.
- No new durable model or Champion has been claimed.
- No PR integration/merge completed in this round; integration remains gated on exact-head checks, genuine receipt, dependency review, concurrent main, code security and postmerge CI.
- Preserve this branch and workflow diagnostic results as-is for subsequent evidence review; do not expand training budget unless resume, complete game, and behavioral gates pass.
