# V7 R001 — atomic claim assignment and P0 #175 review

SESSION_ID=s-20261103-d494b86e; TASK_KEY=coordination/atomic-claim-v1; BASE_MAIN_SHA=c5edec2e3261dacdf3908796ebfe0457fb76c02e; branch agent/s-20261103-d494b86e/optimization-001.

## Inherit/triage

Read the latest V7 Gmail TXT (32,014 bytes) plus AGENTS.md, PROJECT_BACKGROUND, SESSION_PROTOCOL, CLOSED_LOOP, main registry and candidate PRs. Main at initial snapshot contains merged #166 and CI success https://github.com/sstxww/reinforcement-learning/actions/runs/41510861696. #15 is non-Draft but targets agent/learning/v1 rather than main and is stacked on Draft #9; not safe to merge independently. PR #175 implements a no-clobber restore but has an unchecked `samefile`-then-`unlink` rollback race.

## Reproducible P0 finding

Synthetic local race: metadata target exists, first hardlink creates model target; second link fails. During rollback, another writer replaces model target immediately **after** destination.samefile(source) returned true but **before** destination.unlink(). The rollback deletes that other writer's file. Actual local output: `interleaving ['replaced after check'] new writer path exists? False metadata intact? True`. Therefore the current #175 negative test, which races before samefile, does not prove no-clobber throughout cleanup. Review https://github.com/sstxww/reinforcement-learning/pull/175#pullrequestreview-5742272810. No shared file/PR head changes made.

## Isolated implemented improvement

New `scripts/v7_task_claim_d494b86e.py` builds an owner-identifying claim commit from pinned main and performs one GitHub REST POST create-ref for the deterministic SHA256 task key. If ref exists, 422 is a hard failure. It requires readback of the exact newly created commit. There is no force, PATCH, main push, silent race takeover or integration claim. Isolated synthetic tests cover success, collision, readback mismatch, invalid input, and credential fail closed. Branch-only workflow uses a read-only token and at most one pinned-engine eight-seat baseline game.

## Run and remaining gates

Source commit https://github.com/sstxww/reinforcement-learning/commit/e7783b80ee040d4d2ebbe5d90cfe8c808f253354, unique workflow https://github.com/sstxww/reinforcement-learning/actions/runs/41512537092 (initially in progress). The genuine game, if it completes, is seed 97413 / seat 0 / `baseline` only. Do not write a completed receipt until the original Artifact is recovered, and do not call it raw PPO evidence. Own training steps: 0; no new model, optimizer checkpoint, Release or Champion. The official Latest 1408-step candidate has known rank8 behavior and no established paired improvement; additional undirected PPO was not launched. No Arena games.

Next: verify workflow and complete evidence, current-main compatibility, full-match PR CI, and handoff. Neither source commit nor queued workflow implies complete closed loop.
