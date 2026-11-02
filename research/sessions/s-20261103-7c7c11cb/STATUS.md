# V7 Session STATUS — s-20261103-7c7c11cb

**Round:** 001 | **TASK_KEY:** `integrate/postmerge-pr164-schema2-validation` | **Role:** independent postmerge VERIFIER / ARCHIVER, **not** global main INTEGRATOR

**Owned branch:** `agent/s-20261103-7c7c11cb/optimization-001`; original main `3a745c6f6a48c65528bcbeb81b8627b8db93f046`, own branch fork point `990acd21d598a34a554a80c50089a8f1a9423ac4`. Atomic task claim `claims/v7/review-pr164-schema2`; global exclusive integration claim already owned elsewhere. No main merges by this session.

## P0 postmerge evidence
PR [#164](https://github.com/sstxww/reinforcement-learning/pull/164) was merged by **another** session, SHA `990acd21d598a34a554a80c50089a8f1a9423ac4`. Own independent verification: exact PR-head [CI #41511217409](https://github.com/sstxww/reinforcement-learning/actions/runs/41511217409) successful, 373 passed/1 skipped and real TavernGym 8-seat baseline. Exact postmerge-main [CI #41511814464](https://github.com/sstxww/reinforcement-learning/actions/runs/41511814464) successful, 383 passed/1 skipped and full 8-seat baseline. Comment #6586767336 posted to PR.

## Actual training and authentic eight-seat games — verified SUCCESS
Own [Actions #41512463704](https://github.com/sstxww/reinforcement-learning/actions/runs/41512463704) **completed success** on source commit [`f7f13ba0`](https://github.com/sstxww/reinforcement-learning/commit/f7f13ba0d1348f6cdc89b5be14b3d18c1d6812bc). TavernGym 1.1.0 source hash `6d8712c93022ba11`, observe2 4017/447/245. Source registered V2 Release `v2-learning-41413557445`, parent SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, steps before 1280. **Actual MaskablePPO +128 steps → child 1408**, with schema-2 compatibility, increment, SHA-bound metadata, ZIP optimizer & CRC validated.

- Child weights SHA256: `1d2d8aa4dc5210ecead7f75a6d0ca41c6fcbab34461618a05481079dc30100ac`
- Child metadata SHA256: `92cd480f237675c1a284f946d6244cd2de575de71bbc37c4d0b75490b2622c96`
- Genuine own independent baseline seed 43282, seat 0 rank **8**, 19 turns, 43 decisions, placements `[8,1,6,4,2,3,7,5]`, complete, zero truncations; `experiments/s-20261103-7c7c11cb/001-baseline-43282.json`.
- Genuine own raw unassisted model seed 43283, seat 0 rank **8**, 19 turns, 122 decisions, placements `[8,3,5,4,1,2,6,7]`, complete, zero truncations, fallback none, correct child weight digest; `experiments/s-20261103-7c7c11cb/001-raw-model-43283.json`.
- Different seeds: NOT paired; 1 game per policy; improvement **not established**, candidate **rejected**. Never Champion/Best/Latest. No ranked TavernArena.
- Original raw GitHub workflow Artifact ID `13175155239` downloaded & independently verified, but retention 30 days. Exact evidence: `reports/s-20261103-7c7c11cb/001-postmerge-optimizer-and-real-games.json`.

## Release custody / remaining gate
Own run [#41513319168](https://github.com/sstxww/reinforcement-learning/actions/runs/41513319168) for immutable REJECTED model Release `v7-rejected-s-20261103-7c7c11cb-1408-1d2d8aa4` is **queued/pending actual successful publication and redownload verification** as of this STATUS update. Do not claim durable storage until run and Release asset digests pass. No secrets, no write to main/other agents; only own branch, claims and research.

## Next safe steps
Inspect custody workflow run/job logs; for non-success classify exact signature, bounded repair/retest; if success, verify Release API sha256 & compare downloaded metadata and model. Preserve own 8-seat receipts, update this STATUS and PR with exact pointers. Target current main only via PR and independent exact-head CI. Main merge cannot occur without valid exclusive integrator lease and verified latest-head/main gates; hand off to existing integrator. Next research hypothesis: matched-seed raw buy-opportunity and state-progress trace for persistent rank8, not blind PPO scaling.
