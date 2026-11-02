# s-20261102-64405d5e — Round 001: purchase-before-play priority ablation

## Hypothesis / evidence selection
The current `main` baseline prioritizes legal hand-card plays (actions 46–125) ahead of shop purchases (8–15). Test one narrowly defined alternative: when both are legal **and the baseline would play a card**, buy the lowest-index available shop card first. Preserve mandatory choices (30–45), legal masks, and the original 85-action turn safeguard. This is a rule-policy ablation, NOT a PPO experiment.

Base main commit: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`. Session branch: `agent/s-20261102-64405d5e/optimization-001`. Experiment source commit: `82310039db3df863014bf495a855576caba60da5`; test commit: `994e9b27ef44a3c392980f4d6c2679fe78abb015`; workflow run source: `bed855a40eb048088b704c3e80ac9e58139cb44b`. Successful evidence commit: `4323cb40af4101f9a3ffb876c2df63a656624a59`.

### Prior work inspected
- `research/knowledge/INCIDENTS-20261102.md`: full-game PPO safety limit, Release 403, strategy assertion mismatch, excessive workflow reruns; historical clues only.
- Open PR #29 tested upgrade-before-play; #30 tested buy-before-upgrade; #28 tested hold-sell; #32 generic choice-slot bias; #12 sparse vs potential reward PPO failed to improve after 46 matches.
- Our hypothesis is specifically **buy-before-play** with its own new module and no production policy or shared-workflow edit. Other PR findings are unmerged, not promoted to official knowledge.

## Implementation and reproducibility
- Source: `tavern_ai/purchase_before_play_s64405d5e.py`.
- Unit regression: `tests/test_purchase_before_play_s64405d5e.py` (choice precedence, legal purchase, no-purchase fallback, magnetize exclusion, 85-action safety cap, invalid mask).
- Private workflow: `.github/workflows/experiment-s-20261102-64405d5e.yml`, branch-only, 65-minute limit, session concurrency group, trigger path-restricted to this module/tests.
- Real engine: TavernGym **1.1.0**, source fingerprint `6d8712c93022ba11`, upstream pinned commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, verified observe2 patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`; 4017 float features, 447 card indices, 245 legal-masked actions.
- Policy source SHA256: `60592c03c965631d2227528529ee389b3bccfde4d21f76ee68dd03221ca7edbc`.
- Training: **0 gradient steps**. No neural checkpoint, optimizer state or model hash; model_sha256=null.
- Actual GitHub Actions success: [run #41416510547](https://github.com/sstxww/reinforcement-learning/actions/runs/41416510547). **23 tests passed**, engine bootstrap/contract passed, genuine matches and integrity checks passed, result commit and Artifact successful.

## Mandatory independent candidate-controlled full eight-seat match
- Seed **41060**, strategy **purchase_before_play**, one controlled player (seat 0) against seven official scripted TavernGym bots.
- `Game.is_over() == True`, placements **[8,6,2,3,4,7,1,5]**, own rank **8**, decisions **36**, final turn **18**, priority interventions **3**.
- Every chosen action was mask-legal; no truncated combats; no engine turn-limit ending; game guard not exhausted.
- Receipt: `experiments/s-20261102-64405d5e/001-41060.json` (created by run and committed). Not a PPO model match.

## Paired independent evaluation
Six paired seed games (**12 further completed eight-player games**), seeds 41061–41066, original untouched `BaselinePolicy` vs candidate.

| Seed | Baseline rank | Candidate rank | Candidate interventions |
|---|---:|---:|---:|
| 41061 | 7 | 6 | 19 |
| 41062 | 8 | 8 | 4 |
| 41063 | 8 | 8 | 4 |
| 41064 | 8 | 8 | 3 |
| 41065 | 8 | 8 | 5 |
| 41066 | 7 | 7 | 7 |

- Mean rank: control **7.6667**, candidate **7.5000**, candidate-minus-control **-0.1667** (lower is better).
- First-place rate **0/6 both**, top-four rate **0/6 both**.
- **42** candidate action-priority interventions across held-out games. One seed changed rank by one position; five retained equal ranks.
- All 13 real matches ended normally; receipts under `experiments/s-20261102-64405d5e/`, controls under `experiments/s-20261102-64405d5e/controls/`, compact results under `reports/s-20261102-64405d5e/paired-001.json`.
- This sample is **small and near-floor**; no reproducible strength gain is established. No candidate-to-Best promotion.

## Storage and failure state
- Source, tests, 13 compact real receipts, and metrics are in the session branch's Git history.
- [Artifact #13128186981](https://github.com/sstxww/reinforcement-learning/actions/runs/41416510547/artifacts/13128186981) expires **2026-12-02 08:57 UTC**; it is a temporary evidence mirror, not a permanent model checkpoint.
- **No failure occurred in this session's successful run**, so no failure diagnosis is fabricated. Historical incidents were reviewed from actual logs, but belong to other sessions.
- No upstream writes, ranked Arena, shared main-policy mutation, cancellation of others' runs, or permanent checkpoint claim.

## Conclusion and next hypothesis
The conditional buying change definitely executes on real TavernGym game states, but the mean rank delta `-1/6` is not credible evidence of improved gameplay. For round 002 consider stratifying only states where a buy-before-play choice changes shop or hand resource constraints, instrument action sequence and board/hand occupancy, then repeat on more disjoint seeds **only if** the intervention is strategically distinct. A separate model-quality bottleneck is PPO action-loop progress, already under study in other PRs; avoid duplicating their branch edits.

PR and final-head CI status: see this branch's review PR; awaiting integrator approval. Do not merge automatically.
