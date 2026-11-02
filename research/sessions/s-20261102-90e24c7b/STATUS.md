# V5 session status

Session: s-20261102-90e24c7b. Round: 001. Base: main@31dc7c82ad2fcba461706b4f324d743b5c1c2b9e.

P0 actual merge: PR #69 → main commit 31dc7c82ad2fcba461706b4f324d743b5c1c2b9e. Post-merge full-match CI: https://github.com/sstxww/reinforcement-learning/actions/runs/41427702749 (verify latest status before marking complete).
P1: six experimental Releases exist, 1,280-step V2 Release latest documented unpromoted candidate; no proven Champion; main workflow Artifact-only restore is still a gap; do not expand PPO budget.
P2: new opportunity-aware V2 model action telemetry with independent heldout seeds, strict hash gate and real full-game receipts; **execution pending** until workflow completes.
Model promotion: none. New PPO steps: 0. New checkpoint: none.
Scope: isolated source, regression tests, workflow, research and session evidence only.


## Verified execution — 2026-11-02

Dedicated Actions #41428407299 succeeded on source head 5b435034a9091bd544b0f0e84558b3bffef7dd87; engine build, full unit tests, Release V2 SHA256 check, actual six complete eight-seat matches and receipt validator all passed. Evidence commit 84867fb92e3eacc6ca90d45ebcae9111263b203c.
Heldout seeds 89101–89103: Baseline [6,8,8], mean 7.333, selected Buy 41 / 73 decisions with Buy legal, 0 guard forced. Saved 1,280-step V2 model [8,8,8], mean 8.0, Buy **0** / **521 decisions with Buy legal**, 12 forced legal END_TURN guards, 1,087 decisions, no top-four. All game receipts complete, zero simulation truncation. The controlled model has guard intervention, so do not call this raw model completion. Its key behavior defect (no Buy despite legal mask opportunity) is verified for these seeds; global cause (feature/reward/optimizer) remains unproven. No new PPO steps, no new checkpoint, no Champion promotion.
Source report: reports/s-20261102-90e24c7b/001-opportunities.json; real receipts under experiments/s-20261102-90e24c7b/.
