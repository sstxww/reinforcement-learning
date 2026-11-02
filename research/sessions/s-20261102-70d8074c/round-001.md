# s-20261102-70d8074c R001 — P0 triage and durable Release continuation

## Verified setup
- Unique session: s-20261102-70d8074c; branch agent/s-20261102-70d8074c/optimization-001.
- Base main SHA: ef77ae6bc5d9bef09e903fac7705917ec3b7366d.
- Only write target: sstxww/reinforcement-learning; no upstream/official Arena writes.
- Engine: TavernGym 1.1.0 observe2, 4017 features, 447 cards, 245 actions, source 6d8712c93022ba11.
- Latest canonical candidate: v5-s-20261102-68099929-1408-41428692617 (1408 historical steps); weight SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632.
- Champion and Best are null. Published Release alone never proves resumability or performance.

## P0 integration findings
- First open PR inventory returned 75 PRs; only PR #15 was indexed non-Draft. #15 explicitly depends on still-Draft PR #9: no premature merge.
- Reviewed #93: its last-head CI 41429285964 succeeded on an old comparison base, but main registry now has 5 candidates whereas its tests hardcode 4. It also overlaps main release-asset verification. Filed blocking review comment; did not merge.
- Concurrent main updates detected. Recheck HEAD and latest combined CI before any merge.
- Shared train.yml restores a 90-day Artifact and silently initializes random weights when missing. It does not use the Release registry/digests: this is a real P1 training-lineage gap.

## P1 isolated code
- New tavern_ai/verified_resume_70d8074c.py composes canonical registry, two-asset SHA index, strict ZIP/schema1/schema2 preflight, optional genuine one-action inference, and existing MaskablePPO trainer.
- It rejects tamper, unknown IDs, engine/step mismatch, output overwrites and budgets >512. No fallback to random initialization.
- New offline tests and a finite dedicated workflow attempt to prove 1408→1536 optimizer continuation, actual 8-seat baseline+model games, paired evaluation and durable unpromoted Release after validation.
- No modifications to shared trainer, global train.yml, canonical registry, other session files or Champion.

## P2 evidence from other genuine sessions, not ours
- #98: paired V2 model had 42 BUY-legal opportunities but selected 0 BUY; loops in Move/Freeze/Refresh; a forced-END guard; rank 8 against baseline rank 3.
- #103: three heldout seeds 89101..89103 had 521 BUY-legal V2 opportunities and zero BUY; 12 guard-forced END; V2 [8,8,8] vs baseline [6,8,8].
- These rule out the narrow missing-legal-BUY explanation for those tested states; they do not prove a unique reward/optimizer cause.
- Guarded-model completions are not raw-model completions. Do not scale PPO blindly.

## Current handoff
Tests, resumed steps, weight archiving, real games and exact-head CI are pending real Actions execution at this initial commit. Never invent success or receipts. Preserve run logs if any gate fails. New weights must remain unpromoted until validated on independent matches.
