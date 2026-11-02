# Current research status — s-20261102-4d619f26

- Branch: `agent/s-20261102-4d619f26/optimization-001`
- Base main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Original experiment code commit: `f8664511812ebb6eb848d939504892f6140dee70`
- Verified evidence commit: `e4991ffb98a27793bcc0dbd0ab7e4110b8f3e810`
- Draft PR: https://github.com/sstxww/reinforcement-learning/pull/63
- Completed teacher training/game workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41420253632
- PR CI on evidence commit: https://github.com/sstxww/reinforcement-learning/actions/runs/41420953315 — success, independent full TavernGym match and evidence validation.
- Status: **RETEST; candidate is not Champion. No claimed rank gain.**
- Real training: 451 teacher labels, eight supervised epochs, PPO steps **0**; 250 heldout labels, 41.6% exact-action accuracy, 54.8% family accuracy.
- True paired game seeds: 61421 and 61422. Clone ranks [8,8], project baseline [8,7], official teacher [7,4]. Six complete eight-seat games, 0 research-forced end actions, 0 truncations.
- Evidence: `experiments/s-20261102-4d619f26/001-*.json`, `reports/s-20261102-4d619f26/001-summary.json`, `round-001.md`.
- Checkpoint: Actions Artifact `teacher-clone-s-20261102-4d619f26` from run 41420253632, expires 2026-12-02. SHA256 `e46ecc54019df972c45755dea294794e302d51acdb57264c1f5d77180be3d1e7`, restore verified in-run. **Not durably persisted and not a training-resume checkpoint**; replay workflow from fixed seeds to reproduce.
- Current weakness: 3 student BUY predictions versus 42 official-teacher BUY labels on heldout inputs. Missing card identities may contribute but has not been isolated experimentally.
- Next hypothesis: simulator-verified public board/hand/shop card embedding with heldout purchase-recall and paired game evaluation. Avoid simply extending PPO.
- Integration: retain as draft research tool; no model promotion, no main merge, no upstream or ranked-Arena writes.
