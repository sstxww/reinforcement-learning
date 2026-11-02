# V7 round 001 — specific-vs-historical resume proof

Hypothesis: A historical `training_progress.latest_release_resume_verified=true` does not imply that the presently registered 1408-step Release's **own** independent optimizer continuation and downloaded weight load have both been verified. The canonical `latest` record explicitly marks both per-release checks false. Misinterpreting a broad claim can cause agents to skip a necessary safe restore smoke.

Implemented a read-only offline check (`scripts/v7_registry_resume_claim_gate_6c48b19e.py`) and synthetic regressions to distinguish historical from per-model source evidence. It never downloads model weights, trains, or promotes Best/Champion. Even all flags true cannot substitute for an original Release download, SHA check, optimizer load and bounded real continuation.

This is **not** a repair to the global train entry, and the current main may have independent execution evidence not yet reflected in the registry; actual modern Actions receipts must take precedence over stale flags. Compare with merged #117/#161/#164/#165 rather than duplicating changes.

Run only bounded isolated Actions: unit suite focused tests, pinned engine verification and genuine eight-seat **baseline** seed 99573. No result, rank or CI success is claimed before the original workflow finishes and its JSON artifact is verified. No new PPO steps, Release or model quality claim.

Owner files are unique to this session. Global merge privilege not claimed. Next handoff is the exact original run/receipt and latest-head PR CI, followed by integrator review after a new main snapshot.
