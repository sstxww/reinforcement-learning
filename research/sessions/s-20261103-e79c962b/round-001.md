# R001 executed — V7 read-only PR gate and one real baseline

- Initial main SHA `990acd21d598a34a554a80c50089a8f1a9423ac4`, latest observed `c1b828734527bae6141805581693d890cc3bff94` (#165 merged concurrently, not ours).
- Read V7 full 32,014-byte TXT, AGENTS and current train/evaluation/CI/registry. Chose independent preflight rather than duplicated #173/#177/#172 evidence gate or #165 publisher.
- Implemented read-only `scripts/v7_pr_head_audit.py` and synthetic `tests/test_v7_pr_head_audit_e79c962b.py`, 7 local + GitHub tests passed; do not interpret as complete model test.
- Real [Action 41512219188](https://github.com/sstxww/reinforcement-learning/actions/runs/41512219188) at source `209c2904` pinned TavernGym source `6d8712c93022ba11`; verified original Artifact JSON SHA256 `6e7f566039335480737d049a69d11aae59fde3e922d81d6864da293c115826a1`. Baseline seed 99773 seat0 rank7, 14 turns, 44 decisions, eight placement permutation [7,1,8,5,4,6,3,2], no truncated/forced end. This is authentic **baseline infrastructure evidence**, NOT a PPO game.
- Model checkpoint source currently canonical 1408-step unpromoted Release SHA `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` used only as historical reference. New training steps 0, new persistent model 0, no paired model evaluation. Best/Champion unchanged.
- CI nuance: previous-head green is not enough; always verify current branch head and main; script only a preliminary filter. A status of `needs_integrator_review` is **not** merge approval.
- Separate #165 held-out raw evaluation [run 41509707315](https://github.com/sstxww/reinforcement-learning/actions/runs/41509707315) failed `Full-game safety limit exceeded`, publisher skipped, despite an earlier complete rank-eight seed. Do not promote.
- No globally exclusive merge lease was obtained; this session made no main merge. PR latest-head CI and independent integrator review are pending; raw PPO rank-eight cause remains unanswered.
- Next step: review own PR latest-head CI and exact raw receipt, then safely merge only with valid unique integration lease and required checks. No repeat of costly bootstrap on every documentation push.
