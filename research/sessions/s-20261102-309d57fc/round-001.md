# V5 session s-20261102-309d57fc — Round 001: P0/P1 checkpoint audit

## Starting state and safe integration
- Latest 2026-11-02 Gmail "AutoTavern-AI V5" TXT instructions were fully read.
- Only writable repository: sstxww/reinforcement-learning. No upstream or Arena writes.
- Initial main 0cd377e475f1adbea6cf12877d30a97bfb0476e1 (later moved concurrently).
- This isolated branch was created from main 42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c.
- PR snapshot: 68 open / 66 Draft. Main CI run 41424790005 passed on initial main.
- PR #43 head baee34ae58555dfe7dc57725e958881abfc98f87 passed exact-head CI with six independent real eight-seat receipts. Concurrent merge won; my attempted merge was rejected 405 "Merge already in progress"; a subsequent read confirmed #43 merged. Do not credit this session with independent merge execution.
- PR #15 depends on Draft #9; #60 depends on #51; #65 depends on #62. Do not bypass dependency gates or promote their negative models.

## Source-level checkpoint risks
- Main tavern_ai/train.py resumes after checking only JSON engine equality; it does not verify the model.zip SHA256 before deserializing and overwrites the live ZIP before writing metadata.
- Main train.yml primarily restores time-limited Actions Artifacts. It is not a permanent hashed registry.
- GitHub has six published Release entries. Listing their assets and advertised digests does not prove independent re-download, inference or resumption.
- No model currently qualifies for automatic Champion promotion.

## Proposed change on isolated branch
- Add standard-library tavern_ai/checkpoint_integrity.py with streaming SHA256, metadata/algorithm/step/engine checks, ZIP CRC validation, staged save and prior-pair backup, plus explicit CLI.
- Integrate verification before MaskablePPO.load and preserve parent SHA256 and cumulative-step lineage in tavern_ai/train.py.
- Introduce models/registry.json for V1/V2 released candidates with actual hashes and evidence, Champion null, live recovery status pending.
- Add five corruption/resumption safety tests: local Python pytest 5/5 passed; NOT an engine test.
- Add a branch-only 128-step Actions test: download fixed V2 Release, compare digest, verify engine, continue PPO, run model-controlled full eight-seat match, perform two-seed paired descriptive comparison and publish a candidate prerelease only if all stages pass. No automatic Best promotion.

## Evidence-based rank-eight investigation
- PR #15: V1 and 1280-step V2 both had placements [8,8,8,8] on the same four seeds, baseline [7,6,8,8]. Extra steps produced no rank improvement in these observations.
- PR #60: low-LR model had 0 BUY and 21 END_TURN among 36 actions on three heldout full games; its reference had 20 BUY among 875 actions and 21 safety-forced ends. These are genuine recorded counts but NOT legal BUY opportunity rates, and do not prove LR causality.
- PR #65: official scripted bot teacher mean rank 5.10 vs distilled student 7.80 over ten seeds. BC transfer failure is not a candidate improvement.
- Next needed causal measurement: record legal BUY availability conditional on coins/board, actual actions, action loops, fallback, hero/shop confounds, and stage. Defer larger training budgets.

## Limits / next owner handoff
- Local 5-test result is verified. Dedicated Actions run and any new training, games, hashes and Release must be checked independently; no such result is asserted in this initial document.
- The shared trainer modification overlaps Draft PR #9 learning work; reconcile PR #9 and #15 at integration review before merging this branch.
- Keep this PR draft until source review, its latest-head CI and model-controlled full-match evidence pass.
- Never enter ranked Arena, overwrite another session's checkpoints, or claim improved competitive rank from smoke tests.
