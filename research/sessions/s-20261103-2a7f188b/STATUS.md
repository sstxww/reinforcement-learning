# V7 session status — s-20261103-2a7f188b

- SESSION_ID: s-20261103-2a7f188b; ROUND: 001; ROLE: WORKER / code evidence auditor.
- TASK_KEY: `evidence/receipt-git-ancestry`; STATE: running (isolated branch; no exclusive integration lease claimed).
- INITIAL_MAIN_SHA: `3a745c6f6a48c65528bcbeb81b8627b8db93f046`; current main must be refreshed at integration.
- BRANCH: `agent/s-20261103-2a7f188b/optimization-001`; HEAD SHA: follow GitHub PR (changes during evidence commits).
- INHERIT: existing strict receipt integrity and main CI real eight-seat baseline; reviewed PR #164 and #175; recent merged #176; did not rewrite train.yml or other agent branches.
- REVIEW: #164 source-before-learn schema-2 preflight finding posted at https://github.com/sstxww/reinforcement-learning/pull/164#issuecomment-6586679409 .
- HYPOTHESIS: canonical PR receipt validation does not prove a source game's git_sha is reachable from proposed HEAD. Standalone helper detects stale/unreachable claims, never proves gameplay authenticity.
- SCOPE: `scripts/v7_receipt_ancestry_2a7f188b.py`, independent tests and one read-only bounded workflow. Shared gate unchanged.
- WORKFLOW: see `.github/workflows/v7-receipt-ancestry-2a7f188b.yml`; source Actions/run and receipt pending at initial commit, do not claim actual execution before logs.
- MODEL: reused main's indexed 1408-step UNPROMOTED Release `v5-s-20261102-68099929-1408-41428692617` SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, TavernGym 1.1.0 observe2=4017/447/245; no Champion.
- TRAINING: own steps 0; no new model checkpoint or Release; this is a PR evidence audit, not performance training.
- REAL GAMES: workflow planned baseline and one raw-model same-seed canary; no placement asserted until run and receipt independently read.
- EVALUATION: no paired strength claim; all candidate comparisons descriptive only until verified receipts.
- FAILURES: pending workflow execution. Shallow history or missing source SHA are explicit fail-closed cases.
- MERGE: zero PRs merged by this session. No main-integration lease proven; do not call merge API.
- NEXT: inspect the actual workflow run, validate the game receipt and its SHA, commit only genuine receipt, open non-Draft PR, verify exact-head CI and hand to integrator for serialized merge.

## Actual R001 execution / verified immutable evidence

- Branch run [41512480342](https://github.com/sstxww/reinforcement-learning/actions/runs/41512480342) **completed SUCCESS**, but raw PPO model step **failed deliberately tolerated**. All receipt ancestry tests, pinned engine install and baseline step succeeded. Original job 125507560559.
- Own actual baseline: seed 99647, seat0 rank 8, 17 turns, 47 actions, complete permutation [8,2,6,4,1,3,5,7], no truncation; committed at `experiments/s-20261103-2a7f188b/001-99647-baseline.json`. Original file SHA256 f099672d1dc4a42507936dda82c7109557d2ba8ab1806e6fe10e6d88f8bf97bb.
- Exact source Release 1408-step SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632 independently re-downloaded/checksum OK; same-seed raw PPO **did not finish**, `RuntimeError: Full-game safety limit exceeded`, no valid model receipt, no placement. Read `reports/s-20261103-2a7f188b/001-99647-model-failure.json` and `failures/001-raw-ppo-full-game-safety-limit.md`.
- Original 14-day [Artifact 13174760496](https://github.com/sstxww/reinforcement-learning/actions/runs/41512480342/artifacts/13174760496) re-downloaded and byte-verified, ZIP SHA256 9e94de38953603d8aa4543906987801494060d16320fef78239abbaf701b5424; ZIP contains baseline receipt + model-failure status, **not** PPO model weights.
- Additional training 0. No new model SHA, no Release write, no Champion. No same-seed paired model rank difference (raw model unfinished). **Confirmed** only full-game loop bound; root cause remains hypothesis.
- Other sessions independently merged PR #164 (schema-2), PR #165 (least-privilege publishing), PR #176 (FREEZE model telemetry); own merge count 0.
- Current known main `c1b828734527bae6141805581693d890cc3bff94`, same-SHA [main CI #41512315964](https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964) SUCCESS. Refresh before any integration.
- This session has no global exclusive integration lease: no direct merge. Ready to open a **non-Draft** single-purpose PR with authentic receipt, then require latest-head PR CI and independent review. Branch/PR SHA needs refresh after last handoff commit.
- Next owner first action: check exact HEAD CI and review for this PR; compare optional helper with any newer shared gate and, under real serial integration lock only, merge if all checks pass. Preserve raw failure as an uncompleted game rather than ranking.
