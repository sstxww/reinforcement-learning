# Round 001 — genuine TavernGym seat-rotation evaluation

## Reproducibility
- Session: s-20261102-e9dad467
- Base main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Branch: agent/s-20261102-e9dad467/optimization-001
- Code commit: a29d5ecef78e058334a8ea03adaf7c73fd3966e2
- Real receipts commit: 8f54dcb627be0761b59059abf3d4834623c6b2ac
- PR: https://github.com/sstxww/reinforcement-learning/pull/43
- Real GitHub workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41416644671 (success)
- Engine: TavernGym 1.1.0; source fingerprint 6d8712c93022ba11; pinned upstream fb61201a557ddd36a411cf44aac51ce4d9b606ce and patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0
- Observation: observe2 4017 float32 features / 447 int32 cards / 245 legal-masked actions
- Policy source SHA256: e4722a44660f8a880c9eeb949c80e81ebb652926f43d71acd64f958762bd6bac (existing BaselinePolicy).
- Training: none. Actual PPO training steps: **0**. There is no model checkpoint or candidate in this engineering experiment.
- Test result: 15 pytest tests passed in the genuine workflow; no tests were removed.

## Hypothesis and method
Repeated seat-0-only matches can obscure position sensitivity. A new isolated runner controls seats 0, 3 or 6 with the existing baseline and lets seven genuine TavernGym bots control the remaining seats. For each seed and seat, a new real Game is played until Game.is_over() == True; actions are checked against observe2 legal mask, the decision count and full placement vector are recorded, and simulator guards are rejected. A 30000-loop hard cap and 70-minute workflow cap prevent unbounded execution.

The runner stores the self-controlled rank as placements[seat], not the fixed placements[0] that applies only to the original seat-0 canary.

## Real completed matches
All six matches ended with completed=true, zero truncated combats, turn_limit_end=false, TavernGym source 6d8712c93022ba11. Each row has a committed real JSON receipt:

| Seed | Controlled seat | Rank | Decisions | Turns | Receipt |
| --- | ---: | ---: | ---: | ---: | --- |
| 41021 | 0 | 8 | 51 | 16 | experiments/s-20261102-e9dad467/001-41021.json |
| 41021 | 3 | 7 | 49 | 14 | experiments/s-20261102-e9dad467/rotated-41021-seat3.json |
| 41021 | 6 | 8 | 37 | 14 | experiments/s-20261102-e9dad467/rotated-41021-seat6.json |
| 41022 | 0 | 8 | 33 | 14 | experiments/s-20261102-e9dad467/001-41022.json |
| 41022 | 3 | 7 | 76 | 13 | experiments/s-20261102-e9dad467/rotated-41022-seat3.json |
| 41022 | 6 | 8 | 37 | 17 | experiments/s-20261102-e9dad467/rotated-41022-seat6.json |

Compact evaluation: reports/s-20261102-e9dad467/rotation.json. Each seat n=2: seat 0 mean 8.0, seat 3 mean 7.0, seat 6 mean 8.0; every seat top-four 0%, first-place 0%. Overall mean placement 46/6 = 7.6667; 0 top four, 0 first-place across six matches.

## Interpretation and comparison
At these seeds, control seat 3 ranked seventh while control seats 0 and 6 ranked eighth. This supports that the new runner works and catches positional descriptive differences. It does **not** prove a causal game seat advantage, nor does it show policy improvement. Seat assignment changes heroes, potentially RNG paths and opponent context; n=2 per seat is tiny. Existing main fixed-seat baseline remains the comparison reference. No model is promoted to Best.

## Other sessions and prior issues
Main knowledge lists a historically failed PPO safety-limit game, 403 Release permission and strategy assertion issue. Open PRs already explore reward scaling, PPO entropy, upgrade timing, purchasing slots, hero powers, strict receipt validation, and replay; this round only adds separate seat-rotation files and its unique workflow. PR #15 claims genuine 1280-step PPO extension with rank-8 model games and no paired gain; it is still unmerged evidence, not a model promoted by this session.

## Durability and next
Receipts and compact report are committed in this session-owned branch; a redundant Actions Artifact is retained for 30 days (expires 2026-12-02) and is **not** permanent storage. No model weights are created. After review, a held-out seed grid will test whether this descriptive pattern persists without claiming superiority.
