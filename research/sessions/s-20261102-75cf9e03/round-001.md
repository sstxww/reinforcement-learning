# V5 Integration-first R001 — s-20261102-75cf9e03

## Directly verified P0 inventory
- Retrieved latest Gmail V5 TXT (27,248 bytes), read its full contents.
- Authorized repository only: `sstxww/reinforcement-learning`.
- Initial main HEAD `0cd377e475f1adbea6cf12877d30a97bfb0476e1`; 68 open PRs (66 Draft) at first snapshot, rapidly changing due to independent integrators.
- Verified PR #43 seat-rotation and PR #25 receipt integrity were **merged by other sessions during this audit**, not merged or counted as my own integrations. Main advanced accordingly; main CI should be checked per new head.
- PR #8 is Draft and conflicted, with substantial registry/workflow/receipt changes. Posted an integration blocker comment to #8 instead of force-merging. PR #9 remains Draft/unstable and PR #15 depends on #9; none are safe to promote.
- Existing durable Release tags include `v2-learning-41413557445` (model ZIP ~17.5 MB); REST metadata lists assets but **a listed asset is not a verified local download/load/resume**.
- PR #60 (dependent on #51) describes actual model-controlled full games on held-out seeds: low-LR model chose 21 END_TURN and 0 BUY over 36 decisions; comparison logged 20 BUY but 21 forced END_TURN. This is a descriptive **hypothesis** for rank-8 behavior, not a proven causal explanation.

## Concrete own code contribution
- Introduced isolated offline preflight for stored MaskablePPO ZIP plus out-of-band SHA256 and metadata; validates engine fingerprint, contract dims, training steps, safe ZIP structure, CRC, and optimizer archive entry.
- Exposes optional real TavernGym + MaskablePPO one-action inference probe, explicitly distinct from a 128-step optimizer resume and from a complete eight-seat evaluation.
- Synthetic adversarial unit tests cover digest tampering, engine/action mismatch, missing optimizer, absent metadata and invalid ZIP.
- Unique branch-specific workflow runs unit tests and one genuine baseline eight-seat canary, commits only session-owned evidence, never modifies shared main workflow.

## Non-claims and constraints
- **0 PPO training steps, 0 model-controlled games in this round.** No available model assets were independently recovered from Releases or promoted to Champion.
- New code cannot itself cure the policy's rank-8 behavior; correcting action utilization requires proper legality/opportunity telemetry and a verified resumable weight.
- No Arena ranked play; no upstream write; no claim of simulated results before Actions completion.
- PR is deliberately Draft pending final-head CI, real full-match receipt and independent integration safety checks.
