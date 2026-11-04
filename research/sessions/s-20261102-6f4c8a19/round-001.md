# V5 checkpoint integration audit — round 001

- Session: `s-20261102-6f4c8a19`.
- Owned branch: `agent/s-20261102-6f4c8a19/optimization-001`; base main `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`.
- Priority: P0 inventory, then P1 checkpoint verification before any scale-up.
- Initial inventory: 68 open PRs as queried, mostly Draft; main was being independently integrated (notably verified seat evaluation #43 and strict receipt validator #25). This session did not claim or overwrite those merges.
- Historical V2 Release tag: `v2-learning-41413557445`; PR #15 reports 1,280 PPO steps and SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a` with rank 8 in four heldout V2 games. This is historical evidence, NOT this session's verified result.
- New isolated audit utility: enforces release-model byte SHA256, metadata/engine equality, exact step count, loaded PPO observation/action spaces and nonempty optimizer state before continuation.
- A limited, unique Actions workflow will download the versioned Release, run an independent load audit, attempt only 128 additional PPO steps, require full model-controlled 8-player match and paired baseline comparison, then preserve compact evidence and a clearly labeled prerelease if all safety gates pass.
- Test metadata is synthetic fault injection, not a real model, game or training result.
- Current training steps performed **by this session before workflow verification**: 0. Completed real matches **by this session before workflow verification**: 0. No Champion. No production policy promotion.
- Run/receipt/model outcomes must be taken from the Actions run and committed evidence, not predicted here.
- Blocker policy: failed hash, optimizer, engine, download, or full-game gate => stop; retain failure logs, do not create a false checkpoint or blindly expand training.

## Verified experiment completion and negative strategy result

After the schema-2 compatibility fix in `2811ed9`, genuine Actions [run 41428503929](https://github.com/sstxww/reinforcement-learning/actions/runs/41428503929) completed all gates successfully. The verifier checked the actual V2 Release model digest `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, live TavernGym 1.1.0 source `6d8712c93022ba11`, schema2 catalog/ruleset/patch/upstream fingerprints, loaded PPO action/observation shapes and **nonempty loaded optimizer state**.

- Executed 128 extra real MaskablePPO steps from 1,280 to **1,408**.
- Saved new model SHA256 `7703791fe1d7de3951023cdcb9096ee0f8b3808f897cc320a34c15a6627f3401` and metadata in immutable versioned **experimental** GitHub Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-6f4c8a19-41428503929.
- Mandatory baseline seed 68111: rank 8, 57 decisions, 17 turns, full 8-seat receipt; model-controlled seed 68112: rank 8, 123 decisions, 14 turns, full 8-seat receipt, zero simulator protection flags.
- Independent paired seeds [68121,68122]: PPO [8,8], baseline [8,8]; mean ranks 8 versus 8, paired delta 0, top4 and first-place rates 0% both. N=2 is too small to rule in/out small differences, but no signal justifies model promotion.
- Genuine evidence files: `reports/s-20261102-6f4c8a19/001-restore-audit.json`, `001-resumed.sha256`, `001-paired.json` and `experiments/s-20261102-6f4c8a19/001-68111-baseline.json`, `001-68112-model.json`. Reported opponent setup: seven original scripted TavernGym bots; **not** official Arena ranking/MMR.
- The model Release exists and was published by the successful workflow, but the *new* release model's independent re-download and restore were not tested, so distinguish archive creation from round-trip recovery proof.
- **Verdict: REJECT competitive promotion; ACCEPT verified recovery/continuation mechanism as engineering result.** Do not increase PPO budget blindly. Historical PR #60's zero-BUY / 21-END_TURN observation and open PR #98's affordable-BUY telemetry motivate targeted causal instrumentation and phase-conditioned BC.
