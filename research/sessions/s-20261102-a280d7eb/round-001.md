# s-20261102-a280d7eb R001 — V5 PR integration audit + strict paired result gate

## Immutable starting context
- Gmail V5 attachment read in full (27,248 UTF-8 bytes).
- Repository: `sstxww/reinforcement-learning`, isolated branch `agent/s-20261102-a280d7eb/optimization-001`.
- Main at branch creation: `1afd8297e3c661bee3117ac5301b1ca08d64869b` (live main is moving due to independent integrations).
- No direct main edits, no upstream/Arena writes, no model promotion.

## P0: actual integration audit and refusal to bypass gates
- At inspection, open PR count moved from 75 to 74 due to concurrent edits. This is a volatile snapshot, not a stable inventory.
- 74-PR REST snapshot: 73 Draft; only ready PR #15, which explicitly says **do not merge before dependency #9**. #9 remains Draft, with nontrivial shared train/checkpoint changes. Neither is eligible for blind merge.
- PR #91 reported merge conflicts; #84, #86 and #9 reported unstable; Draft #93 and #103 have exact-head successful Actions runs but remain Draft. #93 overlaps functionality already present in main Release asset validation and needs independent overlap review.
- Therefore **zero PRs merged by this session**. Missing author clearance/dependency or exact integration ownership is more important than reducing the PR count.
- Existing main CI on `db5e23ae8c218808821327d806b05d2604cfadfb` was green at run [41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040); subsequent main commits require new exact-head CI checks.

## P1: this bounded implementation
- Added `tavern_ai/paired_rank_gate_a280d7eb.py`, a pure-stdlib read-only reducer that consumes *actual completed eight-seat receipts*, validates strict placement/engine/seed/checkpoint contract, rejects any guarded/fallback candidate result, matches exact seeds AND seats, reports rank/top4/first and deterministic descriptive bootstrap interval.
- Added synthetic-only regression tests; **none of the test fixtures is presented as game evidence**.
- Tool always writes `promotion_allowed: false`; significance and independence must be established separately and no Champion is defined.
- No modifications to shared `train.py`, `evaluate.py`, `models/registry.json`, baseline, other sessions, existing Actions.

## P2: verified observational indicators / causal limit
- Main's `reports/s-20261102-83d91476/001-buy-opportunity-report.json` cites real run [41428098018](https://github.com/sstxww/reinforcement-learning/actions/runs/41428098018): V2 model on seeds 45111/45112 ranked [8,8], had 74 masked-legal BUY decisions yet BUY=0 and 222 of 248 actions were IDs 1/2, with zero forced turn ends. Baseline ranked [6,7], BUY=33 of 48 buy-legal decisions.
- Main's `reports/s-20261102-68099929/003-buy-opportunity.json`: 1408-step candidate seed 99128, rank 8, 35 buy-legal decisions, zero buys; matched baseline rank 8 and 14 buys from 21 legal decisions. Not causal proof from a single game.
- Thus the model's BUY non-selection when legal **is observed**; whether this alone explains rank 8 is **NOT established**. Raw action 1/2 state effects, long-horizon board/economy and reward/advantage diagnostics still require verified probes. PR #107 reports a negative forced-buy ablation and must not be promoted based on its title.

## Train / archive gate (not executed here)
- Canonical `models/registry.json` sets Champion/Best null, Latest to unpromoted 1408-step V5 release `v5-s-20261102-68099929-1408-41428692617`, which has a three-game heldout [8,8,8] rank series. Release presence and recorded SHA are **not** evidence that this session independently re-downloaded, loaded, resumed or trained it.
- Trained steps in this session: **0**. New model checkpoint: **none**. Real games: **pending isolated workflow**. No falsely claimed strength improvement.

## Next checks
1. Execute unique isolated Actions baseline canary and attach its actual receipt; verify unit tests and PR exact-head CI.
2. Recheck latest main/PR conflicts before any integration; do not bypass #9->#15 dependency.
3. Use strict paired reducer on verified raw V2 and Baseline same seed/seat receipts; add controlled/observed Gold and repeated 1/2 action effects before changing reward or expanding PPO.
4. Only after reliable resume + independent raw model full matches and valid matched evidence should a new PPO training budget be considered.
