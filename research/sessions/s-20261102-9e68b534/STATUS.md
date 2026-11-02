# s-20261102-9e68b534 — current status

- **State:** `real_games_verified; PR_pending_review` (not a claim of stronger PPO).
- **Main base:** `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- **Branch:** `agent/s-20261102-9e68b534/optimization-001`.
- **Exclusive source:** `tavern_ai/session_9e68b534_stats.py`; regression tests `tests/test_session_9e68b534_stats.py`; own workflow.
- **Cloud run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415933253 — `completed/success`. Cloud statistical tests passed, pinned TavernGym 1.1.0 hash `6d8712c93022ba11`.
- **Real full matches:** seeds `392500,392501,392502,392503`; seat-0 ranks `[4,6,8,8]`, controlled decisions `[107,50,45,54]` (total 256); `Game.is_over()` reached four times, zero combat truncations, zero turn-limit end, legal actions verified.
- **Receipts:** `experiments/s-20261102-9e68b534/001-<seed>.json`. Metrics: `research/sessions/s-20261102-9e68b534/round-001-metrics.json`.
- **Evaluation:** n=4 baseline-only, mean rank 6.5, win 0%, top4 25%. Bootstrap 95% mean interval [5,8], Wilson top4 interval [0.0456,0.6994]. Insufficient for strength claims.
- **Training:** 0 PPO steps; not a learning/weight experiment.
- **Model:** no model generated; Candidate/Best/Latest N/A; checkpoint N/A.
- **Experiment evidence commit:** `ab2183ba5ffa912074ac2288db3934c76ecb8751` (self-committed by the isolated successful workflow).
- **PR:** to be created against `main`, keep draft pending PR CI review.
- **Failures:** none in this round's GitHub Actions job; a live-running job log fetch returned a transient 404 BlobNotFound before job completion, but final workflow and all steps were successful.
- **Next:** inspect PR CI on final head and review; if first PR CI passes, do not merge automatically. Future research: 30+ held-out paired games for meaningful candidate-vs-control comparisons.
