# Round 001 — V7 source ancestry of real game receipts

**Started from** main `3a745c6f6a48c65528bcbeb81b8627b8db93f046`. A live check found its CI run `41511419671` in progress; earlier main `c5edec2e` CI was successful. #176 was merged by another integrator; no credits claimed here. #164 is non-Draft with a distinct schema-2 metadata bug; posted a concrete pre-learn fail-closed review to its author.

**Proposed change:** independent CLI `python scripts/v7_receipt_ancestry_2a7f188b.py --receipt FILE --head COMMIT --repo .` asserts full local git history and verifies that the receipt's 40-hex `git_sha` is an ancestor of the PR head, after existing strict receipt validation. The tool intentionally returns `authentic_game_proven=false`: logs, Actions provenance and on-policy model hash remain separate mandatory checks. No shared CI or PR admission rule changed. Synthetic tests are explicitly not game receipts.

**P1/P2 boundaries:** official main Release registry records 1408-step experimental model, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, Best/Champion null. Prior raw rank-8, low BUY, FREEZE/REFRESH/HERO/CANCEL evidence does not prove a root cause. We will avoid pointless new PPO steps: own planned +0; run a bounded same-seed real baseline/raw-model comparison in pinned engine only for evidence and tool smoke. No permanent weights/new release claimed.

**Evidence status at authoring:** work is committed only on isolated feature branch, independent Actions not yet observed. No actual seed/placement claimed. Next operator must verify run's exact head, preserve genuine game artifacts, and record any failure without fake rank.
