# Round 001 — masked-mean card pooling ablation

Session: s-20261102-e4c71b9d
Base main: 6ac59235b8238196a0e6462de77b72413c829372
Branch: agent/s-20261102-e4c71b9d/optimization-001
TavernGym: 1.1.0 / hash 6d8712c93022ba11 / observe2 4017+447 / mask 245
Upstream commit: fb61201a557ddd36a411cf44aac51ce4d9b606ce
Patch SHA256: 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0

## Preregistered, falsifiable hypothesis
A card-set mean-pooled branch alongside V1 positional card slots will produce
lower mean rank against seven official bots than the original extractor under
identical MaskablePPO budget. Primary score: pooled minus control mean rank on
identical evaluation seeds; lower is better. Secondary metrics: 8-seat full
completion, legal-action errors, top-four, first-place, per-turn budget fallback,
training time and model checksum.

## Prior knowledge and overlap control
Main research/sessions and research/knowledge/proposals were empty at startup.
Open PR #6 edits baseline, #7 evaluation, #8 infrastructure, #9 learning/canary;
all are draft, not established empirical evidence. This round modifies none of
their files, none of the shared main workflows, and no other session records.

## Reproducibility and resource budget
Dedicated push-triggered workflow under this branch only; 90-minute job limit;
two fresh MaskablePPO models with 128 steps each, seed 32000, n_steps 128,
batch size 64, n_epochs 2, lr 3e-4, CPU 2 threads. Real 8-seat matched
evaluation at seeds 32011, 32012, plus official complete baseline canary
at seed 32010 for an independent receipt.
Command: python -m tavern_ai.card_pool_experiment --steps 128 --seed 32000 --games 2
At 65 seat-0 decisions in a turn, the evaluation wrapper selects legal
end-turn action 0 if available; fallback count is recorded, not hidden.

## Results and limitations
Pending remote Actions execution; no training or strength results are claimed.
The workflow commits compact generated JSON evidence to this session branch;
models are isolated Artifacts with 30-day retention (not permanent storage).
Do not infer comparative advantage from two games.
