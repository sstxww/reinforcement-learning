# R001 — Fail-closed serialized integration gateway

Hypothesis: an unprotected main with many live concurrent sessions needs a single serial main entry, explicit latest-head/base checks, real eight-seat CI confirmation, and actual independent GitHub review rather than old green badges.

Implemented a main-only, manual-dispatch Actions workflow with fixed `autotavern-main-integrate` concurrency; a stdlib-only GitHub API gate checks exact PR number/repo/head SHA and main SHA, non-Draft/clean mergeability, at least one non-author `APPROVED` review **for the current head**, newest successful `pull_request` workflow run started after main's last commit, passing full-match job steps, and last-second SHA recheck. The explicit `execute_merge` input defaults false. If true after these gates, GitHub merges with exact PR head SHA and the job waits for new main CI.

A separate branch push workflow executes gate unit tests and a genuine eight-seat **baseline**, seed 99673; this does not evaluate PPO. Its actual results must be appended after execution and receipt retrieved. The shared trainer, evaluator and model registry are not touched.

Safety limits: serialized workflow cannot prevent out-of-band direct merges; pending dispatches are not FIFO and can be replaced, so this is not a generic lease. No true exclusive integration right claimed. An external review is mandatory: if a single-user GitHub repository cannot supply a different reviewer, record a hard blocker rather than silently disable. Semantic code review, security and branch rules remain required.

Historical evidence: main around 3a745c6f6a48c65528bcbeb81b8627b8db93f046; #176 concurrently merged true 1408→1536 resume with raw model rank-eight. This session added 0 training steps, 0 new Release, 0 model games, 0 model promotions and 0 merges. Pending genuine baseline game evidence: run unknown.
