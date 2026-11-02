# V5 P1 Release and checkpoint registry integration candidate

Session: s-20261102-91b6e4a7, Round 001. Main base: 42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c.
Own isolated branch: agent/s-20261102-91b6e4a7/optimization-001.
Training steps this round: 0. Model checkpoint created this round: none.
No Arena ranked play or upstream write.

## Verified by inspection
- The GitHub Releases API lists the V1 256-step checkpoint v1-learning-9eada5801f99 and the V2 1280-step checkpoint v2-learning-41413557445, each with model.zip and model.metadata.json SHA256 digests.
- PR #9 reports a real model-driven full game for V1 and PR #15 reports PPO continuation from 256 to 1280 and four paired model games ranked 8 each. These are historic run records, not fresh training by this session.
- Main lacked a central models/registry.json at this session's start.
- Issue #78 / PR #60 show a low-LR candidate making 0 buys across 36 actions and a reference with 21 guard-forced end turns and a 40-action identical streak. These are evidence-backed symptoms, not established causes.

## New implementation and checks
- models/registry.json indexes two immutable releases with distinct SHA256s, engine contract and parent version; no Champion or Latest is promoted.
- tavern_ai/checkpoint_catalog.py checks schema, duplicate IDs, provenance URLs, incompatible engine metadata, SHA256, ZIP CRC and model step count without deserializing untrusted model bytes.
- tests/test_checkpoint_catalog_91b6e4a7.py covers rejection of invalid catalog, premature promotion, corrupted checkpoint and changed metadata.
- Live engine-backed smoke workflow is intentionally limited to one real baseline-controlled eight-seat game and this session's own receipt.

## Reproducibility
Run: python -m tavern_ai.checkpoint_catalog
To check a real download: python -m tavern_ai.checkpoint_catalog --model-id v2-learning-41413557445 --weights /safe/path/model.zip --metadata /safe/path/model.metadata.json

A successful SHA256/ZIP/metadata check does NOT show that MaskablePPO.load succeeds or that optimizer state can continue training. Those require separate compatible environment checks. No strength improvement has been claimed.

## P2 root-cause next step
Before spending more PPO steps, instrument legal BUY opportunities, affordable BUY opportunities, model-chosen END_TURN despite affordability, raw action families, public before/after state hashes, and guard overrides per seed. Then compare heldout full games against the same baseline and prior candidate. V2's all-rank-8 paired result does not justify large training.

## PR integration status
Leave integration gated on this session's genuine game receipt, latest PR-head full-match CI, reviewer and main CI. No other session's branch or research files were changed.

## Original baseline full-match gate (executed)

GitHub Actions #41427822784 on head 3cf971c7b037f53a874bfa851a52e00191ce6d97 passed installation, tests, pinned engine and full TavernGym 8-seat baseline-controlled game. Original receipt experiments/s-20261102-91b6e4a7/001-91031.json committed by run in 65bf5ccc1a9f1dfaf7d9fef8aef7f95964cd4826. Seed=91031, rank=8, 14 turns, 51 decisions, complete=true, no combat truncation, no turn-limit guard; model steps=0, policy=baseline. This satisfies the session-owned infrastructure match requirement, not PPO validation. Latest PR CI still needs independent verification.
