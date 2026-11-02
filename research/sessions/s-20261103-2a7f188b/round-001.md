# Round 001 — V7 source ancestry of real game receipts

**Started from** main `3a745c6f6a48c65528bcbeb81b8627b8db93f046`. A live check found its CI run `41511419671` in progress; earlier main `c5edec2e` CI was successful. #176 was merged by another integrator; no credits claimed here. #164 is non-Draft with a distinct schema-2 metadata bug; posted a concrete pre-learn fail-closed review to its author.

**Proposed change:** independent CLI `python scripts/v7_receipt_ancestry_2a7f188b.py --receipt FILE --head COMMIT --repo .` asserts full local git history and verifies that the receipt's 40-hex `git_sha` is an ancestor of the PR head, after existing strict receipt validation. The tool intentionally returns `authentic_game_proven=false`: logs, Actions provenance and on-policy model hash remain separate mandatory checks. No shared CI or PR admission rule changed. Synthetic tests are explicitly not game receipts.

**P1/P2 boundaries:** official main Release registry records 1408-step experimental model, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, Best/Champion null. Prior raw rank-8, low BUY, FREEZE/REFRESH/HERO/CANCEL evidence does not prove a root cause. We will avoid pointless new PPO steps: own planned +0; run a bounded same-seed real baseline/raw-model comparison in pinned engine only for evidence and tool smoke. No permanent weights/new release claimed.

**Evidence status at authoring:** work is committed only on isolated feature branch, independent Actions not yet observed. No actual seed/placement claimed. Next operator must verify run's exact head, preserve genuine game artifacts, and record any failure without fake rank.

## Real execution after the initial branch proposal

- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41512480342 (completed success for engineering workflow); exact source commit `f203b1940b5af72d7f86b872af759f0a0005a36a`. Genuine baseline game seed 99647, seat0 rank **8**, 17 turns and 47 decisions, placements `[8,2,6,4,1,3,5,7]`. Original signed-off complete receipt from Actions Artifact `13174760496` copied byte-for-byte to own `experiments/`. Source SHA ancestry check printed true.
- Source V5 1408-step unpromoted model Release downloaded, verified SHA `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` as original job logs show. Same-seed **raw/unassisted** PPO failed full-match safety limit with no placement; no invalid `model` receipt created. `continue-on-error` was intentional to preserve that exact failure. Explicit JSON failure record under `reports/`, analysis under `failures/`.
- Original Artifact ZIP SHA256 `9e94de38953603d8aa4543906987801494060d16320fef78239abbaf701b5424`, ZIP contains genuine baseline JSON and raw-game-status JSON. Tests and pinned-engine setup successful.
- **Revised hypothesis:** exact source-commit reachability is an independent, meaningful evidence gate, not match authenticity proof; original raw PPO safety-loop failure is confirmed but requires action-transition telemetry to isolate causes. No additional PPO steps or weights were produced. No model promotion.
- **Next:** PR exact HEAD CI plus current-main semantic review; do not merge without real exclusive serialized main access. No ranked play.
