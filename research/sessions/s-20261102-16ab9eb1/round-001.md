# V5 P0→P1 integration: registered Release-bound resume gateway

Session: `s-20261102-16ab9eb1` · Round 001 · Branch `agent/s-20261102-16ab9eb1/optimization-001`
Base main: `1afd8297e3c661bee3117ac5301b1ca08d64869b`.
Source: latest Gmail subject containing "AutoTavern-AI V5", complete 27,248-byte TXT attachment (2026-11-02). Only write repository: `sstxww/reinforcement-learning`.

## P0 integration inventory and concurrency decision

At audit time there were 75 open PRs: 74 draft; #15 was the only non-draft but targets `agent/learning/v1`, not main, and depends on unfinished #9. Main then advanced through several independent merges to `db5e23ae8c218808821327d806b05d2604cfadfb` with successful full-game CI 41432038040. Other integrators subsequently moved main again; always refresh current SHA. #102 already had a live integration-owner claim; do not race another session's target. Avoid wholesale merges of repeated rank-8, recovery and card-catalog diagnostics. This round does not claim a main merge.

## P1 concrete implementation

Existing main includes `models/registry.json`, `tavern_ai/registry_integrity.py`, `tavern_ai/checkpoint_preflight.py`, `train.py` and many model Releases. `train.yml` still relies on 90-day Actions Artifacts and the direct `train.run` path does not require an independently pinned weight digest. No silent fresh restart is authorized as a validated PPO continuation.

Added `tavern_ai/verified_resume_16ab9eb1.py` as an **opt-in isolated gateway** joining the canonical registry with the existing strict archive preflight. It checks exact registered model ID, Release URL, SHA256, ZIP optimizer entries, engine/observation/action compatibility and cumulative steps before any PPO import. Default CLI is **preflight-only**. `--execute-resume` explicitly bounds PPO steps at 128–20000, requires a distinct absent output, refuses source overwrite, audits the resulting archive and writes a lineage sidecar containing the parent/child hashes. No Champion write or auto-release. This DOES NOT replace or claim to fix `train.yml` yet.

Regressions: `tests/test_verified_resume_16ab9eb1.py` uses synthetic ZIP bytes and fake trainer only (not a model-training claim) for hash tampering, metadata mismatch, missing optimizer, conflicting output, missing metadata sidecar, bounded budget, lineage and parent immutability. Dedicated bounded read-only Actions workflow exercises the actual Release bundle and an independent baseline eight-seat TavernGym game.

## P2 evidence-backed rank-8 diagnostic (existing runs, not ours)

- The published V5 1408-step unpromoted model in canonical registry completed held-out n=3 with placements [8,8,8]; same-seed baseline was [6,8,8]. No verified strength gain and no Champion.
- PR #103 reports 521 BUY-mask-legal decision points, **zero purchases**, across 3 guarded V2 games; candidate placements [8,8,8], 12 forced EndTurns. This documents missed legal opportunities, not necessarily strategically valuable cards.
- PR #107 isolated an explicit legal-BUY override causing 46 actual purchases across 3 games, yet all placements remained [8,8,8]. It also observed Play/Cancel cycling. Purchasing alone is not sufficient.
- Already-integrated #108 reports raw V2 seed 87102 stalled at 6000 model actions, 5970 on turn 3 (2978 HeroPower and 2977 Cancel), so this is **not a completed raw-model game**. Opt-in guard completed two paired games but both remained eighth despite 7/6 turns with legal BUY, compared with baseline ranks 5/7. No proof of competitive improvement.
- Hypothesis (not established causal explanation): action representation/progress and valuation fail at multiple stages; test actual turn state deltas, legal BUY opportunities, board size, gold and optimizer learning before further PPO expansion.

## Stage status

Isolated GitHub workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41450004317 (created; live completion must be independently checked).
Own new PPO steps: **0 pending explicit gate**. Own new model-controlled full matches: **0**. No Arena, no new model saved or promoted. Do not claim the synthetic unit tests train a model. Baseline receipt status: pending workflow verification; only commit real generated receipt if it actually finishes.

## Next gate

Verify exact run logs and the Release SHA, actual CPU model load, own baseline full game receipt and matching PR-head CI. If any fail, diagnose and perform at most two meaningful fixes. Once preflight is successful, review integration of this gateway with the existing trainer/workflow without invalidating other Agents' work. Do not start substantial PPO until rank-8 behavior and persistent checkpoint gating are addressed.
