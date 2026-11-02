# s-20261102-b34940b0 — current handoff (Round 002)

**Status:** two genuine full-game rule-policy research rounds executed. Both candidates are **not promoted**; Round 002 final PR CI is required before integration.

- Session: `s-20261102-b34940b0`
- Previous independent [Round 001 PR #32](https://github.com/sstxww/reinforcement-learning/pull/32), latest commit `7f30928a20892fc441bf9c45bc4314daa01d43e1`, [final CI success](https://github.com/sstxww/reinforcement-learning/actions/runs/41416254368); original rules mean 5.75, global last mean 8.0, 4 paired seeds, eight genuine matches. Retain as a negative result.
- Current independent [Round 002 PR #45](https://github.com/sstxww/reinforcement-learning/pull/45) on branch `agent/s-20261102-b34940b0/optimization-002`, based on main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`. Private code commit `a0b692ed302093aadb77a1ad669465b259d02b29`; real evidence commit `f32ce91609518a8d940159b4385236911c1f8c82`.
- [Successful dedicated Actions #41416720643](https://github.com/sstxww/reinforcement-learning/actions/runs/41416720643): 10 unit tests passed, real pinned TavernGym verified, **24/24 full eight-seat games** completed, all own receipts committed.
- Engine: TavernGym **1.1.0**, hash `6d8712c93022ba11`, observe2 dimensions 4017/447/245, seven official bots vs seat0.
- Two seed cohorts: previously explored 65201–65204 and **fresh held-out 65301–65304**. Across all eight per policy, control mean rank **6.625**, global-last **7.875**, posthero-last **7.000**. Top4 fractions **1/8, 0/8, 1/8**; wins **0/8, 0/8, 1/8**.
- **Fresh held-out only:** baseline rank `[8,6,8,8]` mean **7.5**, global-last `[7,8,8,8]` mean **7.75**, posthero-last `[8,7,8,8]` mean **7.75**. All arms top4 0/4. No improvement verified. Overall posthero advantage over global-last largely reflects reused seed 65201 (rank 1 vs 8).
- Genuine candidate complete game `experiments/s-20261102-b34940b0/002-65201.json`: seed **65201**, seat0 **rank 1**, eight placements `[1,7,5,4,3,6,8,2]`, own decisions **52**, turns **14**, zero illegal actions/truncated combats/turn-limit ends; not evidence of an improved policy by itself.
- Actual learning: **0 PPO training steps** in both rounds (two deterministic strategy ablations), no neural weight model or resumable optimizer state. Candidate strategy SHA256 `066666b27049c092be208df2d4e7a3e56e7f5e4f17e8d05f5bed364fdb86b5a1`. Source and receipts are Git-persisted; separate Actions Artifact retention **30 days**.
- Models: no new neural Candidate/Latest/Best; do not promote. Existing independently verified best neural model not established by this session.
- Failure analysis: no execution failure in either round. **Hypothesis not confirmed**: preserving opening hero selection did not improve performance on fresh seeds. Generic `Choose` also includes targets, Discover, etc.
- Read `round-002.md`, `metrics-002.json`, `research/knowledge/proposals/s-20261102-b34940b0-002.md`, raw receipts under `experiments/s-20261102-b34940b0/`.
- Next: gather action-type-specific pending-choice data or evaluate actual card values, rather than fixed slot index. No modifications to other sessions, main, upstream or TavernArena.
