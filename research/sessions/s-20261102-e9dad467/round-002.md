# Round 002 — held-out seat-rotation replication

- Session: s-20261102-e9dad467.
- Branch: agent/s-20261102-e9dad467/optimization-002 (stacked on R001 commit baee34ae58555dfe7dc57725e958881abfc98f87; no changes to main).
- R001 precedent: workflow 41416644671 completed six real games; seat 0 ranked [8,8], seat 3 [7,7], seat 6 [8,8], no top four; n=2 too small to establish effect.
- Research hypothesis: descriptive seat differences on seeds 41021–41022 might disappear or reverse on unseen seeds; collect more independently seeded real games.
- Change: optional --round receipt naming and regression test so R002 cannot overwrite R001 evidence; add own bounded R002 workflow. Shared trainer/baseline/contract unchanged.
- Planned runtime: 12 real complete TavernGym eight-seat matches (seeds 41023–41026 × controlled seats 0,3,6), 70-minute job limit, 30000-loop per match cap, official bots other seven seats, legal-mask validation, no simulator truncation.
- Actual training: 0 steps. Model checkpoint: none (baseline policy evaluation, not PPO). Engine pinned TavernGym 1.1.0 / observe2 4017/447/245.
- Run evidence: pending. Do not claim improvement, win statistics, or run success until actual artifacts appear.
- Expected paths: experiments/s-20261102-e9dad467/002-41023.json and rotated-002-*; reports/s-20261102-e9dad467/rotation-round002.json.
- Evaluation: compare held-out descriptive seat ranks with R001 and aggregate 18 genuine matches if successful; explicitly state tiny sample and hero/RNG confounding.
- Next: only if engine results support, propose testing eight seats per seed and/or model checkpoint with seat-aware placement.
