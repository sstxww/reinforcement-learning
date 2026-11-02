# s-20261102-ecf9aef9 round 001 — P0/P1 integration

Base main (branch creation): \`42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c\`.
Role: independent integration, not Champion promotion or new PPO model.

## Actual audited facts
- Latest V5 Gmail TXT read in full (27,248 bytes).
- 68 open PRs, 66 drafts at initial count. PR #43 and #25 are still open
  but main carries their exact code blob SHA; integrator comments posted.
- PR #15 depends on unmerged draft #9. PR #8 has conflicts plus useful
  historical model registry and Release evidence.
- Main's latest observed full-match gate succeeded on head 0cd377e...
  while another integrator advanced main to 42f4cf3e... during audit.
- Six GitHub Releases show model.zip assets; this session has not retrieved
  weight bytes and cannot claim independent restore of the V2 latest.
- Historical PPO V2 1,280-step candidate placed 8/8/8/8; no Champion.
- PR #60 offers a plausible early END_TURN / missed BUY root cause,
  but legal-opportunity denominators have not been independently collected.

## Extracted change
Read-only \`models/registry.json\` from PR #8, with explicit verification
scope; fail-closed \`tavern_ai.registry_integrity\` and tests; documented
P1 recovery gaps; one bounded branch-only actual eight-seat CI canary.
This avoids modifying the shared main training workflow or resetting models.

## Status and gates
- New neural training: **0 steps**; do not invent PPO continuation.
- Authentic owned full matches: pending independent branch workflow; only
  count as completed after a successful run and validated receipt.
- Checkpoint bytes independently downloaded in this session: **no**.
- Main Champion promotion: **none**.
- Remaining: verify latest-head CI, no duplicate PR merges, review #8
  workflow conflicts, add legal BUY opportunity telemetry, verify Release
  download/hash/load/resume on a dedicated runner before larger training.
