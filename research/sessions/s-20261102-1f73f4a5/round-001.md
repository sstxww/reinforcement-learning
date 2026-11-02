# R001 — real TavernGym public-observation masked behavior cloning

## Identity and sources
- Session: `s-20261102-1f73f4a5`, branch `agent/s-20261102-1f73f4a5/optimization-001`.
- Exact main base `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`; experiment code run SHA `d3a1df791e35169bb986f77a4e66da8445c1b391`.
- Draft PR: https://github.com/sstxww/reinforcement-learning/pull/61; SUCCESS experiment: https://github.com/sstxww/reinforcement-learning/actions/runs/41420063194.
- Main knowledge: `research/knowledge/INCIDENTS-20261102.md` and `docs/CLOSED_LOOP.md`. Unmerged PR #15 reports 1280-step PPO rank 8/8/8/8 vs baseline 7/6/8/8. PR #60 notes low LR PPO did not buy on heldout. These are evidence leads, NOT merged canonical conclusions.

## Actual studied mechanisms
- Verified upstream `crates/taverngym/src/actions.rs` at fixed commit: end=0, refresh=1, freeze=2, upgrade=3; buy=8..15, sell=16..22, activate=23..29, choose=30..45, play=46..125, magnetize=126..195, move=196..244. Legality is from real mask. Most important failure risk is taking legal, non-progressing repeated actions.
- Engine pinned TavernGym 1.1.0, upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, patch `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`, engine source hash `6d8712c93022ba11`, catalog hash `c4c42e6ce5060e1b79fbcd5f4edbf6d17495f0f52690072481d690610f7ef6d7`.
- Model reads only available `observe2` 4017 float inputs, 447 public card indices, current turn and its own action count; masks 245 possible actions. No hidden opponents, future shops or RNG state.
- No claim of understanding card effects, economy optimization or battle positioning; these require independent capability probes.

## Algorithm and reproducibility
- New isolated module: `tavern_ai/bc_s_20261102_1f73f4a5.py`; tests: `tests/test_bc_s_20261102_1f73f4a5.py`; bounded workflow `.github/workflows/bc-s-20261102-1f73f4a5.yml`.
- Teacher: unchanged `BaselinePolicy`; collect from real full-game trajectories at seeds 56100,56101; 113 genuine teacher decisions and 2 completed teacher games [8,7].
- Tiny public-observation student: 96-dimensional float branch + 64-dimensional card embedding branch + masked 245-way classification. Adam LR 0.0006, 5 epochs, exactly **5 gradient updates**; final minibatch loss 2.6092116832733154.
- Heldout seeds 56103,56104, teacher off-policy states 88 decisions; exact teacher-action agreement 0.63636, legal-mask rate 1.0.
- Restored checkpoint from `student.pt` successfully in same run; SHA256: `7be2f5b2a7b2778ce5f3a2a7c0ca4d5c8f79fa0d15e16d83a5ee0e4c71eec669`.
- Artifact `bc-s-20261102-1f73f4a5-model` (ID 13129372107, expires 2026-12-02 UTC); checkpoint **not permanently durable**. No formal Champion/Best.

## True full eight-player results
Each receipt was produced only after `Game.is_over()` and validated. Trainer additionally completed teacher training games, total 6 real eight-player games.
| Seed | Policy | Seat-0 rank | Decisions | Forced end-turns | Combat truncation |
|---|---|---:|---:|---:|---:|
| 56103 | teacher | 8 | 46 | 0 | 0 |
| 56104 | teacher | 6 | 42 | 0 | 0 |
| 56103 | student_bc_guarded | 8 | 214 | 2 | 0 |
| 56104 | student_bc_guarded | 8 | 154 | 1 | 0 |

Receipts: `experiments/s-20261102-1f73f4a5/teacher-56103.json`, `teacher-56104.json`, `student-guarded-56103.json`, `student-guarded-56104.json`; training summary `reports/summary.json`.
Student guarded mean rank 8.0 vs teacher 7.0; paired delta +1.0 **worse** (lower rank number better). Student 368 vs teacher 88 actions on these matched seeds, although legal. This suggests incomplete action-progress competence, not competitive strength.
Guard intervention count = 3; this is BC+guard, **not raw unassisted BC**. N=2 gives no reliable significance assessment or MMR mapping.

## Failure and resolution
Initial PR CI https://github.com/sstxww/reinforcement-learning/actions/runs/41420340906 had 21/21 unit tests pass but failed at independent receipt gate because Draft PR opened before experiment completed. Root cause is submission order, not a Python/test failure. Genuine Action run https://github.com/sstxww/reinforcement-learning/actions/runs/41420063194 has since committed validated receipts at head `5e0f94d67f10841c0ba6f9d561d68eeb136c06d5`. Latest PR CI needs re-verification after this report commit; never replace with dummy receipts. See `failures/001-evidence-gate.md`.

## Decision and integration
**REJECT promotion of this candidate as a stronger model.** Its raw, no-guard completion has not been tested; independent guarded games show worse rank and elevated non-progress decisions. Keep PR DRAFT as experimental mechanism/data plumbing for integrator review; no merge as a performance improvement.
Recommended follow-up: collect a stronger, high-coverage teacher (many distinct economy/turn/synergy states) and train with explicit progress/phase diagnostics; then evaluate pure model vs guarded model separately on many seat-rotated heldout seeds. Do not repeat this tiny 113-sample configuration as proof of learning.

## CI corrective change
- Initial post-evidence CI https://github.com/sstxww/reinforcement-learning/actions/runs/41420778736: 21 unit tests passed, then `validate_receipt` failed on the non-game `experiments/s-20261102-1f73f4a5/summary.json` caught by `check_pr_evidence.py` glob. Fixed by relocating metrics into `experiments/s-20261102-1f73f4a5/reports/summary.json` and staging only real game receipts at the experiment root. Do not weaken common validator.
- Dedicated bounded workflow reruns once after this source/workflow fix; final results and CI require fresh verification.
