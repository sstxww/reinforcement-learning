# s-20261103-5638d3bc — V7 independent raw-model paired probe
- TASK_KEY: eval/v7/raw-v5-1408-seed-1256380
- ROUND: 001; role EVALUATOR; status verified_real_games_pending_pr_ci
- BASE_MAIN_SHA: c1b828734527bae6141805581693d890cc3bff94
- Branch: agent/s-20261103-5638d3bc/optimization-001
- Claim: claims/v7/raw-v5-1256380 (branch creation succeeded; task-only, not an integration lock)
- Scope: own .github/workflows/v7-paired-s-20261103-5638d3bc.yml, experiments/s-20261103-5638d3bc, reports/s-20261103-5638d3bc, research/sessions/s-20261103-5638d3bc, own knowledge proposal.
- Prior related evidence: PR #168 seed 99385 raw 1408-step rank 8 versus baseline 7; no comparative strength conclusion (n=1).
- Model: registered unpromoted v5-s-20261102-68099929-1408-41428692617; SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632.
- Engine: TavernGym 1.1.0, source hash 6d8712c93022ba11, observe2=4017/447, legal actions=245.
- New PPO steps: 0. New model/Release: none. Best/Champion: unchanged. Arena: none.
- Independent seed: 1256380, controlled seat 0; seven scripted bots; raw model vs baseline with exactly the same seed.
- Verified GitHub Actions execution request: https://github.com/sstxww/reinforcement-learning/actions/runs/41513735245 ; push commit 59d821ece38ddf1312ffa5473ba7c24bfda692a5; initial observed status queued, not completed.
- Release independently observed at https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617 with model.zip 17,525,156 bytes and published asset SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632; registered metadata digest 51a651c3a1921447e7bc06c301a52e85331411e75d61b35b5330c43a55aeba9c. Source index does not claim optimizer resume independently tested for this Release.
- Verified NEW OWN genuine completed matched-seed eight-seat games: baseline policy seat0 rank 6, 71 decisions, 16 turns; unassisted model seat0 rank 8, 151 decisions, 15 turns; seed 1256380, 7 native scripted bots, zero truncated combats, no turn limit. Full 1..8 placements retained as unaltered GitHub Actions Artifact originals.\n- New paired delta model minus baseline +2 placements at n=1, NOT a statistical/causal improvement.\n- GitHub Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41513735245 completed SUCCESS on source commit 59d821ece38ddf1312ffa5473ba7c24bfda692a5. Artifact 13174089273 downloaded; ZIP sha256 db237694960aa95a9279588fe58b4d2b3b963128cb65cc68ee780353440b1857. The source run is NOT the subsequent PR head and must not be used as latest-head PR CI.\n- Original model receipt sha256 6d6f614007b454f89f9d1975a4916904a9bb03819039274f3fe6c83070f79667; baseline receipt sha256 7bc8f1725f395114a6127df592ec44e566ed63882583ce2f9a6b309420424997; original paired summary sha256 82efafd7128b4ae17566d314954136c92c512f627352eafe19574f64cd90af44.\n- Original verified receipts: experiments/s-20261103-5638d3bc/001-1256380-{baseline,model}.json; original paired report: reports/s-20261103-5638d3bc/001-1256380-paired-original.json.\n- Follow-up PR requires newly run current-HEAD full-match CI and independent integrator before merge.
- Safety: no main merge, no changes to shared trainer or registry; workflow with finite 45-minute and model 15-minute caps.
- Next: check own push Actions, retrieve original Artifact, validate/commit real receipts if complete; otherwise preserve failure log, then open reviewable PR only after required evidence.

- Related main historical raw model diagnostic synthesis: reports/s-20261103-5638d3bc/001-source-evidence-synthesis.json; no extra games attributed to this session.
