# Round R001 — independent real BUY opportunity replication

Hypothesis: the registered 1408-step raw policy chooses BUY less frequently than a scripted baseline with identical seed, legal masks, seat and engine. This is a falsifiable descriptive claim, *not* an established root cause or an improvement from more PPO steps.

Historical evidence: merged #176 records baseline rank 5 with 18 BUY/25 legal exposures at seed 97303, raw source rank 8 with 0 BUY/23 legal exposures and a distinct 1536-step candidate ranked 8. Those are another session's results, not our run. The merged FREEZE telemetry correction must be reused, not reimplemented. PR #165 owns train.yml privilege changes; PR #175 owns restore atomic install; this task edits neither.

Own fixed seeds: 97421 matched baseline/source; 97422 candidate smoke. Parent SHA256: a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632. Parent is published at https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617. Deterministic CPU model, full eight seats, seven pinned scripted opponents, no forced action intervention, no ranked Arena.

Run: the uniquely named branch-only Actions workflow `.github/workflows/v7-raw-buy-s-20261103-21a7d8bc.yml`; it uses read-only contents permission, 85-minute job timeout, distinct concurrency group and one-shot path trigger. Successful model resume, game completion, rank, model digest, time and Artifact are *unknown until runner reports them*. Artifacts expire in 14 days and must never be labeled permanent. The script tests use synthetic fixtures and are not game receipts.

No claim of strength improvement from n=1; no Best/Champion promotion. Main integration requires latest-head CI, independent game receipts and an actual exclusive integration holder.
