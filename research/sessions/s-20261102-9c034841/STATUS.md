# s-20261102-9c034841 — STATUS (Round 001)

- State: **research candidate evaluated and preserved; performance benefit unproven**. PR/independent CI review required, no model promotion.
- Base main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Branch: `agent/s-20261102-9c034841/optimization-001`; evaluated policy commit: `fea0eb39e6880b732bc2896ca1a47d126fe79de7`; evidence commit: `760aa6cf51ec58e8b80bcfbea3187f72766baf3b`.
- PR: https://github.com/sstxww/reinforcement-learning/pull/30 (**draft**, CI on latest head required, no automatic merge).
- Successful real-engine experiment: https://github.com/sstxww/reinforcement-learning/actions/runs/41415146112 (24 tests, 9 complete games).
- Mandatory candidate game: `experiments/s-20261102-9c034841/001-49101.json`, seed 49101, rank **7**, **45** decisions, 17 turns, no truncated combat or turn protection.
- Held-out evaluation: four seeds [49111,49112,49113,49114], baseline 7.75 mean, candidate 7.25 mean. Top4=0%, first=0% for both. **No proven strength increase.**
- Training steps **0** (rule-policy ablation); model SHA256/checkpoint: none. No Best/Candidate/Latest weight status or resume.
- Engine: TavernGym 1.1.0 / `6d8712c93022ba11`; observe2 4017/447/245.
- Report: `round-001.md`; paired stats `reports/s-20261102-9c034841/paired-report.json`; proposal `research/knowledge/proposals/s-20261102-9c034841-001.md`.
- First failure: 41414939740, mistaken upgrade priority assumption; corrected and verified by successful run 41415146112, see `failures/001-inverted-priority-assumption.md`.
- Action artifact 13126913557 expires 2026-12-02 08:45:35 UTC; Git receipts and compact metrics retained.
- Next: PR review, check latest PR-head CI, independently trace affected upgrade choices; consider more held-out seeds before any strength claim.
