# s-20261102-b34940b0 — verified Round 001 handoff

**State:** `completed_for_review` for the real experimental run; PR head CI must pass independently. Candidate **rejected / do not promote**.

- Session: `s-20261102-b34940b0`
- Own branch: `agent/s-20261102-b34940b0/optimization-001`
- Base main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Independent initial code: `adf99fc8c229f366c8790a904f970643229d7381`
- Real receipts/metrics commit: `51a1ed3212670e18e852327bf774f1678301d4ec`
- [Draft PR #32](https://github.com/sstxww/reinforcement-learning/pull/32)
- [Successful session-specific Actions #41415645714](https://github.com/sstxww/reinforcement-learning/actions/runs/41415645714): 11 unit tests passed; pinned engine installed; eight real complete eight-seat games; all evidence committed successfully.
- Engine: TavernGym 1.1.0, source hash `6d8712c93022ba11`; `observe2` / `4017, 447, 245`; seven official bots per match.
- Seeds: 65201–65204, paired on control and candidate. Control ranks `[4,8,6,5]` mean 5.75; candidate ranks `[8,8,8,8]` mean 8.0, candidate worse by +2.25 rank. Control top4 1/4, candidate 0/4; both win 0/4. No engine guard truncation or illegal actions.
- Completed personal model-free candidate match: seed 65201, rank 8, final eight seats `[8,6,4,5,2,1,7,3]`, decisions 39, turns 15, `completed=true`, `turn_limit_end=false`; receipt `experiments/s-20261102-b34940b0/001-65201.json`.
- Candidate performed 21 multi-option `Choose` decisions across four games.
- Actual PPO steps: **0**, as a rule-policy ablation; no neural model checkpoint, no training continuation / resume state. Candidate policy source SHA256: `bdfba87d599e31e458b575e8156fe8497b5b7724a2d788b42af9f1dc2d6af773`. Baseline source hash: `e4722a44660f8a880c9eeb949c80e81ebb652926f43d71acd64f958762bd6bac`. The Git branch/Commit pin the complete strategy code.
- Saved durable in Git: eight real candidate/control receipts, metrics JSON, source/tests, per-session workflow and this report. Separate temporary Actions Artifact retained 30 days; not needed for rule-policy recovery and not a permanent checkpoint.
- Failures: none in this session run. Other sessions reported economy test assertion failures and PPO nontermination, not reproduced or modified here.
- Important limitation: action IDs 30–45 are **generic `Choose`** actions, including hero choice, Discover, Choose One, target and trinket. Recorded metrics keys `multi_option_discover_choices` are historically named and count generic `Choose` actions, **not only Discover**.
- Current best verified neural model: not established; this candidate is not a neural model and must not replace any Best.
- Next hypothesis: isolate whether hero-selection choices dominate observed rank collapse by restricting choice-slot intervention to non-opening phases, with its own branch and separate seeds.
