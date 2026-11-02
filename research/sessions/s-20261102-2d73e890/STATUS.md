# Final session status — s-20261102-2d73e890

Branch: agent/s-20261102-2d73e890/optimization-001
Base main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
Evidence commit: 9e3620fbd8e7d2e7e553bc71005b935619de1995
Evidence run (success): https://github.com/sstxww/reinforcement-learning/actions/runs/41422154307
PR: see same branch pull request (draft pending CI)
Experiment status: Completed finite mechanism-policy tuning; NEGATIVE heldout strength pilot
Training: 12 complete training-seed games; neural PPO timesteps 0
Evaluation: 16 separate heldout games = 8 paired seeds
Mean heldout placements: baseline 6.375 vs candidate 7.000; higher is worse
Forced end (85 action) = 0; engine guard = 0; 8 candidate receipts persisted
Rules: TavernGym 1.1.0, engine hash 6d8712c93022ba11
Model/checkpoint: none, not a neural training run
Champion: unmodified; recommend REJECT this candidate policy
Primary weakness: blind sale chooses slot 0 without public minion strength, synergy or economy valuation
Resume/reproduce: bootstrap pinned engine; pytest; python -m tavern_ai.sell_cycle_experiment_2d73e890
Next: investigate simulator-backed public card/warband value-aware sell selection without hidden data.
