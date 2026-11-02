# V6.1 R001: Release restore checkpoint no-clobber audit
Owner: s-20261103-f42e91c7, WORKER. Base main 3602f64b798bb51dcf69ef5964fe0b4c4cd39495.
Mail: V6.1 latest message 2026-11-02T19:21:22Z, full 22229-byte TXT read.

## Integration-first evidence
Merged by other sessions: #117 registered Release restore, #125 staged digest checkpoint write, #140 paired receipts, #152 rank permutation, #154 model registry. Our own merged PR count: zero.
Open duplicate Drafts include #165 privilege separation, #166 emergency Release custody, #164 schema-2 metadata, #161 resume guard, #163 action-transition diagnosis; avoided those code paths.
Production train.yml is currently manual-only and Release-based; historical Artifact-only warning from email is not the current main workflow.

## Hypothesis and code
Precheck for nonexistent checkpoint and subsequent os.replace() were non-exclusive, so a second writer could be overwritten. Failure between ZIP and metadata replacement might leave a partial pair. Replace final step with same-filesystem exclusive hardlink install. On ordinary failure, only unlink paths whose inodes still refer to this invocation's verified staged source.
Crash consistency remains limited: abrupt process termination between links can leave an orphan. Startup will fail closed instead of replacing it; manual investigation required.
Six synthetic regression cases cover success, existing model, existing metadata, injected permission failure, post-preflight writer race, and rollback with replaced destination.

## Training, engine, model and evaluation boundaries
Existing parent Release: v5-s-20261102-68099929-1408-41428692617, 1408 steps, SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632.
Engine: pinned TavernGym 1.1.0; observe2 features=4017, cards=447, actions=245, source_hash=6d8712c93022ba11.
Own PPO steps: 0; own model hash/Release: none; own genuine games: 1 baseline (not raw PPO), authentic receipt verified from Actions Artifact. No assisted or raw PPO strength claim and no candidate promotion.
Historical other-session results: 1408-step registered candidate heldout 99125–99127 returned [8,8,8] vs baseline [6,8,8]. Does not prove the cause.
Round executed: isolated read-only CPU tests (11 passed) plus one complete TavernGym baseline eight-seat game seed 94731. Own run: https://github.com/sstxww/reinforcement-learning/actions/runs/41510593830. Artifact 13172278397 was downloaded, SHA256-checked, and the original receipt committed as experiments/s-20261103-f42e91c7/001-94731.json, original JSON sha256 9b22b32b802c75d2b25110ba108cb0d918825af7f8a1f23c8358fd373f996eb2. Rank seat0=6, placements [6,5,4,8,3,7,1,2], 15 turns, 52 decisions, truncated_combats=0, turn_limit_end=false. Independent CI initially passed 343 tests/1 skipped but halted at absence of this receipt: https://github.com/sstxww/reinforcement-learning/actions/runs/41510660778. New exact-head CI required after real receipt is committed. No 128-step training while model behavior gates unresolved.
Receipt is inspected and committed. This PR remains DRAFT pending latest-head CI and independent integration-owner approval.

## Next technical hypothesis
After restore race fix is verified, review raw PPO state/action evidence for whether no-buy symptoms arise before or after action decoding, with new seeds and no forced guard. No next model promotion without independent unguarded completed matches.
