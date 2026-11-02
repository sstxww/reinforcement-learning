# R001 completed evidence: atomic task-claim primitive and P0 race review

SESSION_ID s-20261103-d494b86e / TASK_KEY coordination/atomic-claim-v1 / base main c5edec2e3261dacdf3908796ebfe0457fb76c02e / source SHA e7783b80ee040d4d2ebbe5d90cfe8c808f253354.

## Work actually done
- Read full 32,014-byte V7 Gmail TXT, AGENTS.md, SESSION_PROTOCOL, CLOSED_LOOP, PROJECT_BACKGROUND, current registry and overlapping PRs.
- First-party repo main CI 41510861696 succeeded on original snapshot c5edec2e; concurrent main later advanced to c1b8287 via #176/#164/#165. No ownership claim over those integrations.
- Examined #175's actual patch. Reproduced local deterministic TOCTOU: between `destination.samefile(source)` and `destination.unlink()`, a different writer installs a replacement; exception rollback deletes the foreign file. Visible output: `new writer path exists? False` with metadata intact. Posted [review 5742272810](https://github.com/sstxww/reinforcement-learning/pull/175#pullrequestreview-5742272810). A formal request-changes attempt was rejected because this account authored the PR, HTTP 422. Not a passed review or independently approved merge.
- Created unique deterministic claim branch `claims/v7/coordination-atomic-task-claim-v1`, with explicit owner record, and isolated own work branch; no other branches overwritten.
- Implemented `scripts/v7_task_claim_d494b86e.py`: fresh owner-bound commit + GitHub atomic POST ref + readback; 422 fails closed. Separate offline regression cases for collision, exact-readback, validation and no token.
- Real read-only GitHub Actions [41512537092](https://github.com/sstxww/reinforcement-learning/actions/runs/41512537092) on source SHA e7783b80 succeeded: synthetic tests, pinned engine bootstrap/contract, and one independent full eight-seat TavernGym baseline.
- Recovered actual Artifact 13174011902. Original exact receipt byte SHA256 `ce485a7b24d0757b565486ee821135f75384a172ad54dee3ae5e1e3c968ce64b` and verified `completed=true`, rank permutation, seed, policy, engine hash. Committed **unchanged** to `experiments/s-20261103-d494b86e/001-97413.json`.

## Actual game, not model strength

Seed 97413, controlled seat 0, opponent setup 7 pinned TavernGym scripted opponents, policy baseline, 14 turns, 49 decisions, placements [7,4,2,5,6,8,3,1], rank 7, zero combat truncation, turn-limit forced end false. No new own raw PPO games, 0 PPO training steps, no checkpoint or Release published, no saved optimizer, no statistical inference from n=1.

## Fail-closed limitations and lessons

Task refs are only a one-time anti-collision primitive, **not** main integration execution right. No safe automatic expiration/CAS takeover; do not infer lock exclusivity from a label or branch alone. An integration owner must implement a reviewed merge queue or owner-bound CAS lease before 10-20 agents can merge concurrently. #175's green CI does not prove its rollback ownership guarantee; add regression at samefile/unlink gap before allowing unsafe races to be merged.

## Next

Open non-Draft PR only after original receipt is committed. Verify exact latest head CI and changed-file scope. No merge without independent serialization and full review. Do not start redundant arbitrary PPO training while known raw candidate is rank eight, and never promote unsupported model.
