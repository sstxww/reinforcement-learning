# Round 001 — masked behavior cloning teacher pilot

SESSION_ID: `s-20261102-661adf61`
Branch: `agent/s-20261102-661adf61/optimization-001`
Base main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
Engine pinned: TavernGym 1.1.0, source hash `6d8712c93022ba11`, commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`.

## Prior knowledge and hypothesis
Main `research/knowledge/INCIDENTS-20261102.md` documents stuck PPO complete games and temporary checkpoint/Release persistence issues. Concurrent PRs include PPO learning rate, guard budgets, rule purchase/upgrade priority, seat rotation and rewards; none is accepted as a strong-model result. Instead of another blind PPO run, test whether a small legality-masked teacher-distilled policy can learn the basics of the actual playable action space.

## Mechanisms / leakage guard
Teacher decisions use only `Game.observe2(0)`, `Game.legal_mask(0)`, current public `game.turn` and teacher's own seat-0 decision count; the learner input is only observable `features`, `cards` and `action_mask`. Other seats use engine `bot_play`. Legal-label and no-hidden-input tests are in `tests/test_bc_session_661adf61.py`. Teacher is the repository's simple `BaselinePolicy`, NOT an elite player.

## Bounded experiment (execution is evidence-dependent)
Train full-game teacher seeds: 65101, 65102, 65103. Unseen evaluation seeds: 65901 and 65902. 80 masked supervised gradient updates, mini-batch 64, Adam, 1e-3, CPU. Raw model has an explicit turn-loop failure budget (130 decisions), no fallback. Guarded model chooses END when legal after 85 actions/turn, counting each forced action. Record teacher matched-action accuracy on held-out teacher states and complete eight-seat rank separately. Artifacts are temporary; no persistent checkpoint claim until verified.

## Results
Pending actual GitHub Actions engine execution. **No training steps, game results, model hash, promotion, or finished-game claims are made here yet.** Results will be attached after logs are verified.

## Intended interpretation
A positive imitation accuracy result demonstrates only teacher-action learning, not stronger competitive play. A guarded-only complete game does not count as pure model completion. Compare held-out mean rank, first/top-four rates, and safety interventions with raw model and teacher; n=2 is descriptive only.
