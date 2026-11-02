# Failure 002 — valid 1536-step PPO resume, RAW model cannot complete eight-seat game

## Reproducible primary evidence
- Dedicated GitHub Actions [41451343470](https://github.com/sstxww/reinforcement-learning/actions/runs/41451343470), source workflow head beb8747b4fee1f1946e5056053c6d98a8282d985.
- Exact pinned TavernGym 1.1.0 / observe2 engine fingerprint 6d8712c93022ba11, 4017 float features, 447 cards, 245 masked actions; real engine installed successfully.
- Own real *baseline* match seed 73021: completed in 16 turns/61 controlled decisions; seat 0 rank 6; placements [6,1,5,8,2,7,4,3]; 0 combat truncations. Source receipt actually committed on own branch at experiments/s-20261102-70d8074c/001-baseline-73021.json.
- Verified BOTH actual downloaded V5 source Release assets and strict ZIP/engine/step metadata. Source version v5-s-20261102-68099929-1408-41428692617 (1408 steps), weight SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632.
- Executed **128 actual additional PPO optimizer steps** on the real engine to cumulative **1536**, verified new ZIP and metadata, and passed actual CPU one-action model inference both before and after training.
- Generated weight SHA256 **ba0b0fef382f4e277f55e606e5f5e0e64ec3659da9bde68a5130f72882fffada**. Metadata SHA256 **cf25c7ff092d2b21a6af0cb85f4e8c06ada154671a52d4b3a3599d25d2b0362b**.
- Full compact training report in failed run Artifact [13144677554](https://github.com/sstxww/reinforcement-learning/actions/runs/41451343470/artifacts/13144677554), temporary storage only; do NOT call it durable.
- Original **raw model** full eight-seat match seed 73023 ended with Python RuntimeError **Full-game safety limit exceeded** at tavern_ai/canary.py:54 after the 30000-iteration safety guard. No final placement, no match receipt. The paired heldout evaluation and original workflow's gated Release step were rightly skipped.
- Raw-model failure is not a rank-8 match. It is a verified action-progression defect for this source/model/seed, consistent with independent #98/#103/#107 no-BUY and loop behavior.
- **No Champion, no Best, no demonstrated game improvement.**

## Root-cause boundary and next controlled test
A single incomplete raw-model match cannot identify a unique causal defect in reward, optimization, legal masking, mandatory choices or gameplay policy. The known exact external reason is that the raw deterministic action sequence did not complete before 30,000 engine loop iterations. Existing #107 forced-BUY treatment yielded 46 legal buys with no rank gain and many Play/Cancel cycles; avoid another blind buy override or simply increasing PPO budget.

Next hypothesis: measure Play↔Cancel reversal, Freeze/Refresh repetition, exact public-state changes and legal BUY opportunity/selection on **fresh seeded model-controlled episodes**, with raw and guard-assisted outcomes separately named. Reject any proposed change that does not measurably reduce loops and improve raw full-game completion.

## Recovery/persistence response
The raw-game failure must not cause loss of validated optimizer state. An isolated *new* bounded workflow [41452421637](https://github.com/sstxww/reinforcement-learning/actions/runs/41452421637) attempts to **recover exactly the already-run weight bytes** from the failed Actions Artifact, verify both SHA256 values and CPU inference, then publish a unique GitHub prerelease **explicitly named REJECTED/UNPROMOTED**. It does not continue training or mark the model a success. Verify the new run and roundtrip release hashes before claiming durability.
