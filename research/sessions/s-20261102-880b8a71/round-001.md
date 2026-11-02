# s-20261102-880b8a71 — V5 R001: integration-first Release recovery audit

## Scope and actual GitHub work

- Base main commit: `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c` (queried before branch creation).
- Own isolated branch: `agent/s-20261102-880b8a71/optimization-001`.
- Owner-approved repository only: `sstxww/reinforcement-learning`; upstream TavernGym and official Arena are untouched.
- Full 27,248-byte V5 instruction attachment was read from the newest matching Gmail message.
- Added isolated `scripts/verify_release_resume_v5_880b8a71.py`, regression tests, and one bounded GitHub Actions workflow. Shared trainer, baseline, evaluation, README and other sessions are unchanged.
- Real workflow URL: https://github.com/sstxww/reinforcement-learning/actions/runs/41427593167
- **At authoring time: workflow queued. Training steps actually confirmed from this session: 0; real games actually confirmed from this session: 0; new checkpoint: none. Never treat workflow configuration as successful execution.**

## P0 integration findings and priority order

Starting inventory: 68 open PRs, six GitHub Releases, main `0cd377e475f1adbea6cf12877d30a97bfb0476e1` with green CI 41424790005. Main advanced concurrently. PR #43 (verified seat rotation) and PR #25 (strict receipt audit) were merged by **other** actors at `2ac79f258211356989a6ecbbb4a5614617290bd8` and `f29a0a6e99161aca4163e51427f6bfabbe02f76f` respectively. They are not this session's merges; final main CI must be observed independently.

Review targets:
- #8 infrastructure: Draft, observed mergeability conflict; modifies shared `train.yml`, model registry, validator, and README. Rebase/cherry-pick minimal recovery/storage tooling rather than blind merge.
- #9 learning V1: Draft, shared `train.py`/canary changes, its 256-step model exists as unpromoted Release; current-head check runs missing at inspection. Needs compatibility and independent recovery tests.
- #15 learning V2: non-Draft but depends on #9 and cannot safely merge ahead of that parent.
- #51 and dependent #60: real low-LR PPO negative experiments with action-telemetry evidence; preserve diagnosis but do not promote weak model or blindly merge full stacked experiment.
- #25: independent evidence validator with successful latest-head PR CI; since integrated by another actor, do not duplicate it.
- #43: six real seat-rotated games, last-head PR CI passed; since integrated by another actor, do not duplicate it.
- #72/#76: stacked sell-swap experiments, fresh held-out gain not proven; keep as research evidence, not strategy promotion.
- #77: candidate had zero held-out interventions; no competitive improvement demonstrated.

No unreviewed Draft was flipped to ready and no direct main push/unsafe concurrent merge was performed.

## P1 source checkpoint, independent Release recovery gate

Source candidate: GitHub Release `v2-learning-41413557445`, reported 1,280 MaskablePPO steps, SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- Verified existence of the GitHub Release API listing model.zip (17,525,115 bytes) and model.metadata.json (932 bytes). **Asset existence alone is not an independently verified download/hash or successful resume.**
- Existing unmerged infrastructure registry calls it `Latest` experimental and `Best = null`. The registered four held-out model ranks are [8,8,8,8] compared with rules baseline [7,6,8,8]. No Champion.
- Current main `train.yml` restores from expiring Actions Artifacts and does not fall back to Releases. Current main `train.py` writes schema-1 metadata. Our isolated release gate verifies source zip SHA256, exact cumulative 1,280 steps, TavernGym 1.1.0 fingerprint and schema-2 source provenance *before* attempting load.
- The workflow attempts exactly 128 extra PPO steps to reach 1,408, then writes SHA256 and provenance to the resumed metadata, runs one model-controlled full eight-seat game, three paired independent held-out seeds 27100–27102 versus baseline, and *only on success* publishes a uniquely tagged **unpromoted** GitHub Release, then independently re-downloads both model assets and compares bytes.
- No score or restoration success is claimed until Actions evidence becomes completed and successful.

## P2 rank-eight causal audit: observed versus unknown

Two independent sources, not proof of a single causal explanation:
1. Latest durable v2 1,280-step PPO experiment, run 41413557445, shows 4/4 model rank 8 on seeds 24000–24003; baseline ranks [7,6,8,8]. This is a tiny sample and not evidence of model improvement.
2. PR #60 real 256-step PPO action telemetry, three held-out seeds 42174–42176: low-LR candidate rank [8,8,8], action categories 21 END_TURN, 12 mandatory choices, 3 hand plays, **0 buys over 36 actions**. Reference rank [8,8,7], 20 buys but 788 `other_action` events, 21 guard-forced END_TURN and maximum same-action streak 40 over 875 actions. Both completed real games. Full report: `reports/s-20261102-24728f13/002-action-telemetry.json` on PR #60, engine `6d8712c93022ba11`. This is a different checkpoint, so do not transpose exact statistics onto v2.

These observations distinguish an early END_TURN/buy underuse hypothesis from reference nonprogress loops. Missing measurements: gold and legal BUY opportunities, true state transition progress, start-of-turn board strength, action mask provenance, and controlled-seed mechanism tests. We cannot yet conclude that low learning rate caused the issue. More PPO steps are **not justified as a performance intervention**; our bounded 128-step run is a recovery mechanics smoke test, not a strength claim.

## Reproducibility and next gate

- Use private workflow `experiment-s-20261102-880b8a71.yml` on the source branch. Independent concurrency; writes only own evidence and optional immutable Release; no official Arena.
- Unit tests use synthetically generated ZIP fixtures and cannot count as real model games.
- Actual model ZIP and complete-game receipts must originate in GitHub Actions and have matching SHA.
- Follow up by reading the terminal run status, job logs, source model SHA, and genuine receipt. If the run fails, record failure and avoid fake reports. Do not increase training unless behavior tests and paired games support it.
