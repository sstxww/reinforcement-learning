# Round 001: potential-based reward shaping

Session: s-20261102-bf8e1710
Base main SHA: 6ac59235b8238196a0e6462de77b72413c829372
Training branch: agent/s-20261102-bf8e1710/optimization-001
Execution commit: a1658e2fc8fd64e8c5220970b4d9f0c19000546f
PR: to be created by the research agent after this workflow completes
Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41414320347

## Hypothesis and prior evidence
Original TavernGym SoloEnv returns zero on nonterminal legal steps and a
placement-only reward at termination. A discounted, bounded, *public-observation*
potential may provide a more learnable signal during short CPU PPO training.
Main has no merged experimental session results at start. Open PRs #6-#9
remain unverified research leads; their owned modules were not changed.

## Exact change and reproducibility
New opt-in tavern_ai/reward_shaping.py wraps TavernEnv; the shared train.py
and train.yml remain unchanged. Formula:
Rshaped = Rraw + gamma * Phi(next) - Phi(previous); Phi(terminal) = 0.
Phi uses self-health, armor, tavern tier, and board count at global float
offsets 5, 6, 10, 32; no hidden state. gamma=0.99, same as PPO.

Command: python -m tavern_ai.reward_experiment --session-id s-20261102-bf8e1710 --steps 256 --seed 33123
Each arm uses 256 real TavernGym environment steps; total 512.
Two matched seed runs, original sparse control vs potential reward, same network
and fixed evaluation seeds [33011, 33012, 33013]. Model: MaskablePPO MultiInputPolicy.
Engine: 1.1.0; hash: 6d8712c93022ba11.
Upstream commit: fb61201a557ddd36a411cf44aac51ce4d9b606ce.
Engine patch SHA256: 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0.
Observe2: 4017 features, 447 card slots, 245 masked actions.
Full config and model hashes: research/sessions/s-20261102-bf8e1710/round-001-metrics.json.

## Actual held-out results
Control placements: [8, 7, 8]; mean rank 7.667;
top-four 0.000; first-place 0.000.
Potential placements: [8, 7, 8]; mean rank 7.667;
top-four 0.000; first-place 0.000.
Potential minus control mean-rank delta: +0.000
(equal); sample only 3 paired seeds. No statistical strength claim.

## Mandatory separate genuine eight-seat match
Receipt: experiments/s-20261102-bf8e1710/001-33001.json
TavernGym game reached Game.is_over() == True; seat-0 model rank
8, full placements [8, 4, 2, 6, 1, 7, 5, 3]; seed
33001; decisions 359; turns 15.
Illegal actions: none accepted by legal-mask driver; combat truncations
0; turn-limit flag False.
Model safety fallback: at most 48 decisions per turn before a legal
end-turn (or forced mandatory choice); overrides: 7.
Independent of the common PR CI canary.

## First attempt: failed game-progress guard
GitHub Actions run 41413409487: the sparse-control model trained 256
real PPO steps but its unbounded policy failed to finish seed 33011
within 30000 scheduling rounds. No model match receipt existed for
that attempt. This revision applies the same per-turn 48-action
fallback to *both* arms and logs the override count. Baseline seed
33000 was a valid completed match, rank 8; retained independently.

## Checkpoints and limitations
Model SHA256: 58c6c924f49b86ef97d13712b8a97c1d7b80bcede632d885ce316edb9a3611e5
Storage: dedicated s-20261102-bf8e1710-round-001 GitHub Actions artifact (90-day
retention, NOT permanent); workflow run https://github.com/sstxww/reinforcement-learning/actions/runs/41414320347.
Files in artifact: checkpoints/s-20261102-bf8e1710/control/model.zip and
checkpoints/s-20261102-bf8e1710/potential/model.zip.
To restore an arm: download its exact-run artifact, verify SHA256 from the
metrics JSON, and use MaskablePPO.load(path, device="cpu") with the pinned engine.
Temporary rollout and vendor build files are not committed.
One train seed, extremely small budget, three games per arm. Improvement,
if observed, is unconfirmed; false improvement due to chance is plausible.

## Next round
Test 2-3 additional independent training seeds, >=30 paired held-out
game seeds per arm and confidence intervals; increase training steps only
with isolated budgets. Retain any negative result as knowledge.
