# s-20261102-cacfdbae — V5 R001 STATUS

**State: verified engineering restore and bounded real continuation; model not promoted. PR integration CI still separately gated.**

- Branch: `agent/s-20261102-cacfdbae/optimization-001`; original main base `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`.
- PR: https://github.com/sstxww/reinforcement-learning/pull/81
- Successful independent real workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41428441545
- Failure and repair: https://github.com/sstxww/reinforcement-learning/actions/runs/41427542987 (historical schema2 metadata); fixed in commit `94723a1`.
- Real MaskablePPO continuation: original 1280 -> **1408** total, **128 additional** steps, seed 61102. Source V2 SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- True model-only games: seed23002 original rank8 (134 decisions), resumed rank8 (134 decisions); both completed with zero truncated combats or simulator turn limit.
- Independent paired evaluation (n=2; seeds24000/24001): resumed model [8,8], baseline [7,6], mean delta **+1.5 worse**. No improvement claimed.
- New checkpoint SHA256: `f0d9c459b9a96e45c206f2a00196d3d7d3c887bb6fb907918c17c8e3010a2b39`.
- Published durable unpromoted Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-cacfdbae-smoke-128 — assets `resumed.zip`, `resumed.metadata.json`; verify downloaded bytes and metadata before any future resume.
- No verified Champion. `models/release_inventory_v5.json` is a separate read-only inventory, avoiding overwrite of PR #8's registry.
- All evidence in `experiments/s-20261102-cacfdbae/` and `reports/s-20261102-cacfdbae/` committed by successful workflow `41428441545`.
- `train.yml` on main still uses finite-retention Actions Artifacts; actual unified main workflow recovery remains unproven and unmodified here.
- Latest automated PR CI after bot evidence commit was `action_required` with no jobs; do not treat it as successful. A final source-authored commit should trigger actual CI before any merge.
- No Arena ranked matches, no optimizer/weight overwrite of other sessions, no large-scale training.
