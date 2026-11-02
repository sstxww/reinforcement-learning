# V5 session s-20261102-902968f5 — verified work and limitations

**State:** `P1_resume_verified_P2_loop_reproduced_P3_guarded_pilot_pending`. Mainbase `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`; development lives only on own branch `agent/s-20261102-902968f5/optimization-001`. [Draft integration PR #84](https://github.com/sstxww/reinforcement-learning/pull/84). **Do not merge/promote without final code tests and interpretation of real results.**

## Completed P0 integration audit
- Read latest V5 Gmail attachment in full, README/AGENTS/protocol, main trainer/evaluator/canary, 68 initial open PRs, six Release assets.
- Other integrators merged PR #25 (receipt integrity), #26 (replay audit), #43/#47 (seat/paired evaluations), #37 (uncertainty) while this session was running; this session did not duplicate or claim those merges.
- PR #8 infrastructure/registry conflicts with concurrent main; PR #9 source training hardening and dependency PR #15 V2 still require independent integration checks. Shared `main` trainer / train.yml / model registry untouched by this session; automatic Release restore remains unimplemented in main.

## Successful P1 Release, checkpoint and training evidence
- Source experimental Release [v2-learning-41413557445](https://github.com/sstxww/reinforcement-learning/releases/tag/v2-learning-41413557445): old checkpoint `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a` (1280 PPO steps), metadata digest `6f0b433191a8242dcedc627f6be49d1551a82788ce7bfd8e60416ede8146acc0`.
- Actual dedicated [run 41427679320](https://github.com/sstxww/reinforcement-learning/actions/runs/41427679320): pinned engine and unit checks success; downloaded exact Release assets, verified both checksums, loaded optimizer and sampled legal prediction; **genuinely continued 128 PPO steps, 1280 → 1408**. Resumed new checkpoint SHA256 `503c527492d3a43ff2be9996c4865d2af8be55a981a5a0308b4dccb316598e8e`. Report `reports/s-20261102-902968f5/001-resume-audit.json`.
- Own baseline full 8-seat seed **927103** completed, seat 0 rank **8**, 15 turns, 37 decisions, no truncations, receipt `experiments/s-20261102-902968f5/001-baseline-927103.json`. Baseline is NOT a PPO or guarded-model win.
- **Pure resumed-model 8-seat seed 927104 FAIL**: `RuntimeError: Full-game safety limit exceeded` from `tavern_ai.canary.py`. No completed PPO receipt, no valid placement for that run. Documented `research/sessions/s-20261102-902968f5/failures/001-unfinished-model-game.md`. The original workflow properly finished with conclusion **failure**, despite successful training step.
- New 1408-step checkpoint now saved as clearly [Rejected GitHub Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-rejected-1408-902968f5) via [successful Action 41428795631](https://github.com/sstxww/reinforcement-learning/actions/runs/41428795631): model and metadata re-downloaded, SHA256 checked, same engine loaded, optimizer exists and legal inference worked independently. This is durable versioned Release storage, not offsite backup or Champion. No deletion of earlier weight.
- CI full-match gate **success** on PR commit `da93c232758f1e49418616764382abb523dea8ff` and again on `d3dd62bbebf646cbb4b7eae28e6de5d47a7b6843`; recheck final head after later changes. Original early CI failure was missing own-session receipt before cloud job committed it; 92 tests passed at that time.

## P2 evidence: model Play→Cancel loop is reproduced
- Dedicated [run 41428534974](https://github.com/sstxww/reinforcement-learning/actions/runs/41428534974) **success** (instrumentation succeeded, **model game incomplete**). Real checkpoint 1408 SHA checked and same failure seed 927104, native TavernGym.
- Model made **301 decisions**, **300 in turn 1**, **0 actual BUY**, **0 END_TURN**, **7 decision points with a legal BUY mask**. Raw replay shows repetitive `Play(46)` → `Cancel(7)` actions; the native pinned action mapping in PR #75 identifies action 7 as Cancel. Board count in the public float feature remained 0; diagnostic stopped at per-turn decision guard 300 with `completed=false` and **no fabricated placement**.
- Trace `reports/s-20261102-902968f5/002-public-action-trace.json`; full historical P2 report `research/sessions/s-20261102-902968f5/rank-eight-root-cause.md`. This proves a concrete early-game stall for this checkpoint/seed, not a general explanation of every rank-eight result.
- Historical PR #60 corroborates different model pathologies (0 BUY + early EndTurn vs large no-progress loops) and PR #15 shows 256→1280 extra training on four seeds did not improve rank. No statistical strength claim or promotion.
- Caveat: native mask can force Cancel after invalid Play targeting; we must not suppress Cancel without an alternative action. Distinguish policy loop from an upstream engine bug pending extra targeted tests.

## P3 isolated single-hypothesis study (pending)
- `tavern_ai.play_cancel_guard_902968f5` implements **changed policy**: when a Play is immediately Cancelled, temporarily masks that failed Play ID within the same turn if another *native-legal* option exists; never suppresses sole legal Cancel, invents actions or forces END_TURN. Finite genuine TavernGym seeds 927104 (historical failure control) and 927106 (new) in branch-specific [Action 41429333809](https://github.com/sstxww/reinforcement-learning/actions/runs/41429333809), state pending at this record.
- Results will be labelled `guarded_model_play_cancel_blacklist_not_pure_PPO`, NOT pure-model canary receipts. No new PPO training in P3, no promotion unless held-out and seat rotation prove sustained rank improvement. If no game completion, report `completed=false`.

## Files and next gate
`research/sessions/s-20261102-902968f5/round-001.md`, `round-002.md`, `rank-eight-root-cause.md`, failure report, P1/P2 diagnostics and P3 reports on own branch. Actual source model and resumed model are retained in immutable versioned GitHub Releases; only source V2 had a real complete historical model game. Champion/Best **unassigned**.

Next: evaluate P3 completed-vs-incomplete and intervention counts; if promising, run paired multiple independent seeds/seat-rotation without fallback and only then consider a proper learned policy update. Merge reviewed non-overlap infra separately from speculative guard; no Arena ranked, no upstream writes.
