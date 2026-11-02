# V5 integration session s-20261102-490e3c78 / R001

## Scope and integration evidence
- Latest Gmail V5 TXT read in full, with P0→P2 first.
- Explicit repository: sstxww/reinforcement-learning; no upstream or official ranked Arena writes.
- Initial main SHA observed `0cd377e475f1adbea6cf12877d30a97bfb0476e1`; 68 open PRs at initial snapshot.
- Independently inspected PR #25 strict receipt validator: genuine three-game receipts, six synthetic negative cases, entire 29-test latest-head PR CI success; current main advanced concurrently.
- PR #25 was marked ready and squash merged as commit `f29a0a6e99161aca4163e51427f6bfabbe02f76f`; post-merge main CI [41426899067](https://github.com/sstxww/reinforcement-learning/actions/runs/41426899067) **success**. This is a data integrity improvement, not a competitive win.
- PR #8 has a wide conflicting draft covering the registry, cleanup, workflows, training and other shared files. This R001 branch selectively preserves only its historical candidate registry with separate fail-closed offline validation; it does **not** merge PR #8 or change the shared trainer.
- No automatic Champion designation.

## Evidence-backed rank-eight leads
- [PPO PR #60](https://github.com/sstxww/reinforcement-learning/pull/60): on three genuinely heldout full games, 1e-4 candidate rank 8/8/8 with 36 decisions, 21 chosen END_TURN, **0 purchases**; 3e-4 reference rank 8/8/7 with 875 decisions, 20 purchases, up to 40 consecutive identical actions and 21 forced endings. The zero-buy behavior is established; its cause (legal-buy opportunity, economics, reward, masking) is **not** established.
- [BC PR #65](https://github.com/sstxww/reinforcement-learning/pull/65): 10 heldout games per arm showed official teacher mean rank 5.1, student 7.8, V0 baseline 7.5; limited imitation transfer is observed despite teacher action samples including 61 buys.
- [V2 PR #15](https://github.com/sstxww/reinforcement-learning/pull/15): a genuine continuation from 256 to 1,280 total PPO steps had identical poor four-seed ranks 8/8/8/8; durable Release exists but V2 independent Release→resume is not yet verified.
- Root-cause hypothesis, NOT proven: a collapsed policy action distribution and insufficient economic behavior may dominate the early rank failures. Next discriminating experiment must count legal BUY opportunities and compare model policy at the same observations before changing reward or scaling steps.

## Own verification scope
- Current R001 branch base: main `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`.
- Additive model index + ZIP/hash/metadata preflight and unit tests.
- An isolated workflow is responsible for a real baseline-controlled eight-seat canary receipt in `experiments/s-20261102-490e3c78/001-59001.json`; do not treat it as executed until its Actions run succeeds and the file exists. This canary is engineering evidence, not a PPO model test.
- Additional PPO training steps **0** in this round; independent latest V2 checkpoint byte download/restore/inference **not run** by this session. Scaling blocked by unresolved P1–P2 gates.
- This draft is for independent integration review, not direct main push.
