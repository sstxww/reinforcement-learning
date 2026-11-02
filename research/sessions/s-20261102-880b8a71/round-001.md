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

## Actual completion addendum — verified after first failed raw game

1. **First run** [41427593167](https://github.com/sstxww/reinforcement-learning/actions/runs/41427593167) reached Release SHA verification, **1,280→1,408 real PPO steps**, hash `0c871559bde9fabd6700b5d015ab3b4424222d37204e32bfdaba93b028e89e3e`, but raw seed 23051 `RuntimeError: Full-game safety limit exceeded` (not complete); 58 Python tests passed. No game receipt/new Release. Temporary Artifact ID 13132134365, expires in 30 days. Failure detail: `research/sessions/s-20261102-880b8a71/failures/001-unbounded-model-action-loop.md`.
2. **Second corrected diagnostic run** [41428666321](https://github.com/sstxww/reinforcement-learning/actions/runs/41428666321) completed **SUCCESS**. All Python tests, engine, checkpoint checks and independent 128-step PPO continuation passed again; this run's model SHA256 is **`ce9b73b5eea8eedccfcdd48c59105e829dbb20a4e8aa8e3dce6c7f6210a2c980`**, total 1,408 steps. This is not the first run's SHA; always pin run and model identity. Its **temporary** model/metrics Artifact ID 13132798706 is slated to expire 2026-12-02 10:28 UTC; no immutable new Release because raw full-game gate failed.
3. **Raw no-fallback probe** `23051`: 600 actual model decisions, `Game.is_over()=false`, turn 7 had 502 actions, and 28 decisions exposed a legal BUY slot but selected BUY **zero** times. This is an incomplete raw probe (no rank; no completed game receipt). First 32 actions repeatedly include ID 1 (**Refresh**) and ID 2 (**Freeze**); exact action family verified against merged `tavern_ai/mechanics_audit_s_30b45c4d.py` (PR #70). 344 actions are presently aggregated as `other` in the experimental classifier, so do not equate all of them with refresh/freeze without raw action IDs. `observation_progress` counted 592 comparable pairs but no exact identical consecutive public observation hashes; lack of identical hashes is not proof of meaningful board/economy progress.
4. **Guarded model (not raw)** completed four genuine TavernGym eight-seat games seeds `23051/27100/27101/27102`, ranks **[8,8,8,8]**; forced legal END_TURN counters **[1,3,2,0]**. Paired original scripted baseline on `27100/27101/27102` had ranks **[8,6,7]**. Guarded candidate matched-rank deltas **[0,+2,+1]**, mean **+1.0** worse; n=3 only, not a statistically conclusive strength effect. The model had no positive outcome and cannot be Champion.
5. **True evidence committed** on this branch: `experiments/s-20261102-880b8a71/001-23051.json`, `paired-{27100,27101,27102}.json`, `reports/s-20261102-880b8a71/behavior-001.json` and `resume-attestation.json`; own experiment run passed. These are clearly labelled `policy=guarded_model`, `raw_model_only=false`, hash-matched. Original baseline paired results are embedded in the report (not fabricated raw PPO matches).
6. **Independent PR CI** at 41429081015 is `action_required` with **zero jobs**, not green. Before receipts, CI failures had identified missing independent game receipt. Latest PR remains DRAFT; no main merge or official game. This is an external execution/approval state, not a proven code failure on the newest head.
7. Next single-factor candidate: test a **fixed refresh/freeze repetition circuit-breaker**, with accurate action family counts and only public state/mask, against three new seed-rotated batches; require raw unassisted completion before any model promotion. Do not blindly expand training budget because the current 1,408-step policy is behaviorally pathological.
