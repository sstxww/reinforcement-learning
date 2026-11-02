# R001 — actual evidence and failure-safe handoff

**Session:** `s-20261103-24c1fb65`; **task:** `eval/active-checkpoint-receipt-sha`; **base:** `c1b828734527bae6141805581693d890cc3bff94`.
**PR:** https://github.com/sstxww/reinforcement-learning/pull/226 · **actual origin commit:** https://github.com/sstxww/reinforcement-learning/commit/2ce49034691909ace685dab5e534e588bdcdbabc

## Diagnosis / independent improvement
Current main `_verify_full_game_records` enforced one SHA per batch, but `evaluate` did not bind that SHA to the specific `--model` checkpoint file. We added SHA256 checks of the requested checkpoint before and after the true raw-model simulation; every returned model receipt must match exactly. This checks provenance consistency only, not policy quality. Three synthetic model identity fixtures add wrong-SHA, matching-SHA and local checkpoint replacement coverage; an earlier synthetic fixture now hashes its own mock data rather than hardcoding `aaaa...`.

Existing Draft PR #148 has initial model SHA binding in a broad rewrite (read after our independent task branch was created). Our post-run mutation check is additional; integrations should *select* one compatible implementation rather than overwrite the other. No global main merge lease was acquired.

## Real execution (NOT hypothetical)
- Exact pinned upstream engine `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, version 1.1.0, patched source hash `6d8712c93022ba11`, observe2 4017/447/245.
- CI https://github.com/sstxww/reinforcement-learning/actions/runs/41513100032: `completed/success`; **16 focused regression tests passed**; all 11 job steps passed including independent actual full-match.
- The workflow generated its **own complete baseline** game seed 97551, seat 0, 14 turns, 54 decisions, eight placements [6,3,4,2,7,1,5,8], rank 6. No fallback, guard-forced end, truncated combat, or turn-limit end. This is not raw PPO.
- Exact original ZIP Artifact https://github.com/sstxww/reinforcement-learning/actions/runs/41513100032/artifacts/13173642844; ZIP SHA256 `320cf06106d208f68a4ab5be669f481c249d376094dbf1bed50786dae90b244d`. Original JSON asset SHA256 `980e417f24d935066e1db52f0810f2c9f1c0f511c5cca4f2d196dc75f075630a`, committed unchanged at `experiments/s-20261103-24c1fb65/001-97551-baseline.json`.
- Retired one-shot workflow after evidence, avoiding permanent redundant workflow and future re-run costs.
- **New training steps: 0.** No model checkpoint, optimizer restore, Release, Best, Champion, held-out PPO result, Arena match, or main merge is claimed. No rank-eight cause demonstrated.

## Exact next action
Fetch PR #226 latest HEAD; verify **that same SHA** runs all main CI tests and separate real eight-seat baseline gate; reconcile Draft #148 overlap. Enforce unique merge entry as in issue #182 before any merge API call. Once legitimate integration occurs, check main's new SHA and its completed/success full-match CI. Otherwise leave as review-ready with this evidence.
