# s-20261102-2acfa761 · Round 001: integration-first, real game and model rank-8 evidence

## P0 audit and concurrency
- Original main HEAD at branch creation: `1afd8297e3c661bee3117ac5301b1ca08d64869b`. Main moved repeatedly while agents integrated other PRs.
- Found 74 open PRs in a snapshot, 73 Draft. Only non-Draft #15 was stacked on agent/learning/v1, dependent on Draft #9; not directly safe for main.
- Reviewed PR #93: exact-head CI green but stale fixed four-model assertions on branch, while current main has five candidate checkpoint entries and a canonical two-asset verifier. Added review comment https://github.com/sstxww/reinforcement-learning/pull/93#issuecomment-6577792804; did not merge a redundant/unsafe draft.
- Integration PR for this isolated contribution: https://github.com/sstxww/reinforcement-learning/pull/115 . **Remains Draft.** No changes to other sessions, main, upstream, or Arena.

## P1 engineering delivered and executed
- Created `tavern_ai/paired_evidence_v5.py` and `tests/test_paired_evidence_v5_s-20261102-2acfa761.py`. Tests intentionally synthetic (not game evidence); check seed identity, completed full-game receipts, source hash, policy provenance, no mixed model hashes, and paired game-level uncertainty; never claim Champion.
- Original full eight-seat TavernGym baseline-controlled seed **96271**, Actions run **41449769964 SUCCESS** (https://github.com/sstxww/reinforcement-learning/actions/runs/41449769964), generated committed `experiments/s-20261102-2acfa761/001-96271.json`: control seat 0 rank **6**, placements [6,2,1,3,8,5,7,4], 15 turns, 52 decisions, 0 truncated combats, no turn limit.
- Added independently bounded isolated workflow `.github/workflows/paired-existing-evidence-s-20261102-2acfa761.yml`, verified successful Actions run **41450465518**, which actually executed `python -m tavern_ai.paired_evidence_v5` over six pre-existing authentic eight-seat TavernGym receipts for matched seeds 99125–99127 and archived resulting `reports/s-20261102-2acfa761/001-actual-1408step-paired.json`. Raw 1,408-step model SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` gets ranks [8,8,8]; same-seed Baseline [6,8,8], paired rank delta [2,0,0], mean +0.667 worse, exploratory bootstrap interval [0,2]. No strength gain demonstrated.

## P2 rank-eight diagnosis
Evidence from existing main `reports/s-20261102-83d91476/001-buy-opportunity-report.json` and `reports/s-20261102-68099929/003-buy-opportunity.json`:
- V2 candidate: 74 decisions with BUY mask-legal, 0 purchases in 2 completed games; 222/248 actions chose Refresh or Freeze (pinned IDs 1 and 2).
- 1408-step candidate: another game had 35 BUY-legal decision exposures, 0 model buys; reference baseline 14 buys/21 such exposures.
- This rules out 'BUY never mask-legal' for *these sampled states*, but does not isolate causal root (reward/logits/normalization/action choice). Turn-level exposures are not independent sample sizes. See `eighth-place-diagnosis.md`.

## Integration and training/retention gates
- No merged PRs by this session. Original PR CI #41449977814 passed 244 unit tests and had 1 skip but failed evidence because our independently generated receipt had not yet been committed. Following branch bot commit triggered an `action_required` CI (#41450058813); do not claim latest HEAD CI success. Current main/PR head must be rechecked before any merge.
- We used existing Release checksum metadata and actual main records, **did not download/resume/checkpoint** a PPO model ourselves. GitHub Releases exist; we do not claim independent Release restoration for this session.
- Own model training steps **0**, new model-only games **0**, model weights published **none**, Champion status **null**, no official Arena scored play. P0/P1/P2 still need consolidated final integration and action policy causal fix; bulk PPO therefore intentionally not started.
- Next: obtain final HEAD CI, review PR #115, merge only when gates actually pass, instrument raw masked logits/legality/economy/public-state progression on fresh independent games and run one minimal legal action intervention. If validated, perform limited checkpoint-verified PPO, evaluate and archive before scaling.
