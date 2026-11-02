# V7 round 001 — specific-vs-historical resume proof

Hypothesis: A historical `training_progress.latest_release_resume_verified=true` does not imply that the presently registered 1408-step Release's **own** independent optimizer continuation and downloaded weight load have both been verified. The canonical `latest` record explicitly marks both per-release checks false. Misinterpreting a broad claim can cause agents to skip a necessary safe restore smoke.

Implemented a read-only offline check (`scripts/v7_registry_resume_claim_gate_6c48b19e.py`) and synthetic regressions to distinguish historical from per-model source evidence. It never downloads model weights, trains, or promotes Best/Champion. Even all flags true cannot substitute for an original Release download, SHA check, optimizer load and bounded real continuation.

This is **not** a repair to the global train entry, and the current main may have independent execution evidence not yet reflected in the registry; actual modern Actions receipts must take precedence over stale flags. Compare with merged #117/#161/#164/#165 rather than duplicating changes.

Run only bounded isolated Actions: unit suite focused tests, pinned engine verification and genuine eight-seat **baseline** seed 99573. No result, rank or CI success is claimed before the original workflow finishes and its JSON artifact is verified. No new PPO steps, Release or model quality claim.

Owner files are unique to this session. Global merge privilege not claimed. Next handoff is the exact original run/receipt and latest-head PR CI, followed by integrator review after a new main snapshot.


## Completed original execution and permanent evidence handoff

Original GitHub Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41512975850 completed **SUCCESS**, job `125509224054`. Python focused regression passed, registry provenance audit completed, exact TavernGym 1.1.0 bootstrapped, and authentic full eight-seat **baseline** match finished before the original report artifact was uploaded. Full original Artifact `13173872617` downloaded and ZIP members parsed rather than inventing new receipt data.

Baseline only: seed 99573; controlled seat 0 rank 7; ranks `[7,2,4,1,3,5,6,8]`; turns 17; decisions 36; true complete, no combat truncation, no turn limit forced end. Immutable source head `fddefa9740eda6c2f0a40f80c3e466ed4d4fc760`; receipt bytes SHA256 `5f30d7b6d1a69bf3c2c461d853ef844b63be233a4c8e18ec80ef7a27df543719`. Copied to `experiments/s-20261103-6c48b19e/001-99573.json` from original own Action. No raw PPO model was controlled: **0 PPO steps**, **0 new weights/optimizer**, **0 model Release**, **0 model-controlled games**, **0 player Arena games**.

Source registry report `reports/s-20261103-6c48b19e/001-resume-claim-audit.json` original JSON SHA256 `ad04dbee87b7b196c162bade367a78c74b4f2de855294b71ad5e038f4ba76fa2` recorded historical resume=true but current 1408-step model-specific independent resume=false and load-from-downloaded-Release=false. Hypothesis demonstrated at **metadata consistency** level, not proof that historical resume never occurred. Independently testing checkpoint optimizer state remains the next experiment for its own unclaimed task; don't duplicate or overwrite another live worker.

After success, retired session-only push workflow by `2522f0ba846e70f9137e13eccd59128137238339` so no automatic repeat and no new persistent workflow on main. Existing verified model remains the registered V5 1408-step *unpromoted* Challenger; no strength improvement established. PR https://github.com/sstxww/reinforcement-learning/pull/200 is the isolated delivery. As the session lacks an exclusive serial merge lease, maintain review status until real latest HEAD PR CI + integration authorization and postmerge main verification. Next round: compare same SHA against live model restore evidence to distinguish registry documentation lag from a missing independent smoke, not increase PPO steps just to claim progress.
