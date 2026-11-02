# s-20261102-75cf9e03 — Verified R001; bounded R002 submitted

- **R001 independent workflow success:** https://github.com/sstxww/reinforcement-learning/actions/runs/41427453982
- **Unit tests:** 87 passed on first R001 HEAD; independent preflight tests included. First PR CI failed solely because session-owned receipt had not yet been committed.
- **Genuine R001 eight-seat baseline receipt:** `experiments/s-20261102-75cf9e03/001-65810.json`, seed 65810, **rank 8**, 33 decisions, 16 turns, placement [8,7,1,6,5,4,2,3], complete=true, 0 combat truncations, 0 turn-limit ends. This is baseline, **not PPO**.
- **R001 tests:** static synthetic archive guard, SHA/metadata/ZIP checks, optional inference probe; no checkpoint claim.
- **R002 new workflow:** `.github/workflows/resume-smoke-s-20261102-75cf9e03.yml` triggered by unique-file branch push; downloads V2 experimental Release, verifies published SHA256, probes model inference, attempts exactly 128 PPO incremental steps, checks 1280→1408, then requires genuine model complete eight-seat game before any unpromoted diagnostic Release is published.
- **R002 outcome:** pending actual Actions logs. Do **not** claim resumed, archived, match complete or model improved unless supported by a successful run.
- **Champion:** None verified. Existing V2 release is unpromoted. No Arena ranked.
- **Source baseline commit for R001:** `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`; first code commit `56e0452ed9618284a1cf73d886d77bcf7dd77912`.
- **Research PR:** https://github.com/sstxww/reinforcement-learning/pull/79 remains Draft until fresh latest-head CI passes and integration review. 
