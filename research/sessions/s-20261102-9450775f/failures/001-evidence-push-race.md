# Failure 001 — concurrent branch advancement rejects Actions evidence push

- Signature: `git push origin HEAD:$GITHUB_REF_NAME` rejected non-fast-forward (`fetch first`).
- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41427478915
- Job: https://github.com/sstxww/reinforcement-learning/actions/runs/41427478915/job/125217484244
- Source SHA (run checkout): `c2eb34d1f8f62eb2600ec55619a09cc5bb7532b6`
- Cause: own research PR_AUDIT.md was committed on this branch after the run had checked out the earlier SHA, so GitHub refused the stale checkout's evidence commit. This was not a TavernGym, test or model inferencing error.
- Tests, engine installation, Release model download/hash, full model-only 8-player game, baseline 8-player game, and Artifact upload **all passed**. The overall workflow status is **failure**, solely in the final evidence push step.
- Artifact: https://github.com/sstxww/reinforcement-learning/actions/runs/41427478915/artifacts/13132303660 (30-day retention; not permanent storage).
- Recovery: downloaded artifact ZIP and committed exact `reports/s-20261102-9450775f/model-gate.json` and `experiments/s-20261102-9450775f/001-945078.json` to the same branch with GitHub Contents API. No fake matches or rerun-as-success.
- Model: V2 Release `v2-learning-41413557445`; SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, 1280 stored metadata training steps, compatible TavernGym 1.1.0, optimizer presence and ZIP CRC verified.
- Real model seed 945077: **completed**; rank 8; 122 decisions, zero BUY, 37 legal-BUY decision opportunities, 41 REFRESH, 71 OTHER, 7 END_TURN, 1 UPGRADE, 2 CHOOSE; zero forced END or baseline fallback, no truncation. No causal attribution from a single game.
- Independent baseline seed 945078: **completed**; rank 8; 39 decisions, 15 turns, positions `[8,5,7,1,3,2,6,4]`.
- Prevention: the workflow's final evidence commit must fetch/rebase remote branch with a finite retry budget (or use a safe upload process) because this single-session branch may advance with its own docs. Never force push and never touch other Agents' branches.
- One meaningful fix is planned next; no blind duplicate SHA reruns.
