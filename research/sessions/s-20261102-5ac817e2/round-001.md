# s-20261102-5ac817e2 R001 — V5 P0/P1 main-training continuity safety

## Integration audit
- Start main HEAD: `1afd8297e3c661bee3117ac5301b1ca08d64869b`, after concurrent integrations advanced earlier `db5e23ae...`.
- At first snapshot 75 open PRs; 74 Draft, only #15 non-Draft and stacked on unmerged Draft #9. Therefore **zero PR merges were safe from this review**. #93 and #103 stay Draft; no merge bypass of their final-head gates.
- Actual main CI on `db5e23ae...` at Actions #41432038040 succeeded. No claim about our new head CI until it runs.
- Main registry exists with `best=null`, `champion=null`. Release-backed unpromoted 1408-step latest was recorded with heldout [8,8,8], no model promotion.

## Exact identified P1 failure
The existing `.github/workflows/train.yml` silently removed the checkpoint and reinitialized PPO when the most recent successful main Artifact download failed. GitHub Artifacts expire. This could reset training progress while pretending to provide incremental continuation.

## Code changes proposed (review required)
- Fail closed if an existing successful main run has no downloadable complete checkpoint.
- Only allow *first ever* model initialization from an explicit manual `fresh_start` input; never from a scheduled run or a missing old Artifact.
- Run a read-only archive/engine/optimizer metadata preflight before continuing. Without independent trusted SHA, report `external_sha256_verified=false`; a successful preflight is NOT proof that PPO loaded or training resumed.
- Add 12 synthetic offline tests for corrupt metadata/hash/ZIP/optimizer and schema-2 compatibility.

## P2 causal evidence status
- Independent PR #103 reports genuine V2 guarded model [8,8,8], **zero BUY in 521 BUY-legal decision states** (n=3), guard-forced END_TURN 12. This is evidence of missed legal opportunities, not proof all purchases were optimal or proof of a specific reward bug.
- Independent PR #95 reports V2 resume +128 steps with paired ranks [8,8] before and after and zero buys. Further bulk PPO has no demonstrated gain.
- Actions from the current session: **0 PPO steps**, **no new weights**, **no new ranked matches**. Our real baseline canary receipt and branch CI must be confirmed separately; do not infer a success from this document.

## Next integration gate
Inspect exact-head PR CI and own game receipt, main concurrent changes and review ownership. The main workflow still needs a deliberate, externally SHA-pinned Release fallback integration before claiming unattended long-term resumability; do not automatically select an unpromoted latest candidate as Champion.
