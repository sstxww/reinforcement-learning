# AutoTavern V5 — s-20261102-fda20934 / round 001

## Scope and provenance

- Only writable repository: `sstxww/reinforcement-learning`.
- Started from `main@1afd8297e3c661bee3117ac5301b1ca08d64869b` on 2026-11-02.
- Isolated branch: `agent/s-20261102-fda20934/optimization-001`.
- Source instruction: owner's V5 Gmail TXT; P0 integration before P1 training, P2 root diagnosis.
- No changes to other agents' branches, model releases, upstream engine or official ranked Arena.

## P0 real inventory and integration gate

GitHub open PR collection returned **75 open PRs: 74 Draft, one non-Draft (#15)**. The non-Draft #15 expressly depends on Draft #9; therefore it is not eligible for standalone merge. This inventory is a point-in-time observation, not a lock; rerun before merging.

- **A / candidate for strict review**: infrastructure tests and Release integrity PRs such as #93, #84, #83; currently Draft, and latest-head checks/concurrency reviews are required, so zero approved merges in this session.
- **B / repair first**: #9 and dependent #15; #91/#94 previously reported conflicts; confirm latest heads and CI before any integration.
- **C / further evaluation**: #93, #86, #91, #103, #107 and #105; distinguish exact latest-head CI and fully completed model-vs-baseline games. #107 stacks on #103; #105 stacks on previously described #90, so never merge stacked work blind.
- **D / negative or unproven experiments**: #12, #16, #18, #61, #65, #71 and several strategy ablations. Preserve genuine failure evidence but do not promote their candidate policy.
- **E / overlapping candidates**: Release/registry/preflight work in #82/#83/#84/#86/#92/#93/#94/#95 overlaps existing `models/registry.json`, `tavern_ai/checkpoint_preflight.py`, `tavern_ai/registry_integrity.py` and release evidence on main. Prefer a targeted minimal integration over replacing canonical data.

Main CI on `db5e23ae8c218808821327d806b05d2604cfadfb`: [successful run 41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040). Main moved to `1afd8297...` before this branch; success on an older head is not success for the newer head.

## P1 concrete code change

On main, `.github/workflows/train.yml` previously deleted unavailable Artifact remnants and continued with a **random new model** without an explicit user decision. This breaks cumulative training lineage.

This branch introduces:
- `tavern_ai/resume_gate_fda20934.py`: refusal on missing or partial checkpoint pairs unless a *manual* workflow dispatch explicitly allows a new run; checks checkpoint archive bounds, ZIP/optimizer entries, metadata/engine contract, positive cumulative steps, and metadata digest if present.
- `tests/test_resume_gate_fda20934.py`: eight offline cases covering incomplete pairs, missing artifact, authorized fresh start, tampered weights, invalid engine contract, corrupt ZIP and nonpositive step count.
- Updated `.github/workflows/train.yml`: scheduled training **cannot** silently create random weights on failed Artifact recovery; manual `allow_fresh_start=true` is required to intentionally start from scratch.
- A uniquely scoped GitHub Actions evidence job executes unit tests and a real pinned-engine eight-seat **baseline** match, then commits its real receipt only to this session branch.

Limitations: a legacy metadata file without SHA cannot prove byte provenance. This gate does **not** itself resolve permanent Release fallback, optimizer continuation or fair competitive evaluation. Do not present it as complete unified model storage.

## P2 evidence-backed eighth-place diagnosis (read-only main reports)

- Main `reports/s-20261102-83d91476/001-buy-opportunity-report.json`, authentic [run 41428098018](https://github.com/sstxww/reinforcement-learning/actions/runs/41428098018): V2 model finished 2/2 true games at [8,8], had 74 *legal BUY decision states* and chose BUY 0 times; 222/248 actions had raw IDs 1 or 2. Baseline same seeds [6,7], 33 buys; no forced ends. It establishes that failure is **not** merely an absent legal BUY mask.
- Main `reports/s-20261102-ba09e2d4/002-action-opportunities.json`: raw V2 policy on one uncompleted probe produced 2,978 hero-power and 2,977 cancel actions by a 6,000-decision budget, no buys; this is **not** a valid placement result.
- Main `reports/s-20261102-68099929/003-buy-opportunity.json`: separate genuine single paired game, model 0 buys on 35 legal-buy states vs baseline 14 buys on 21 states; both ranked eighth. Limited sample; not causal proof.
- Main `models/registry.json`: at inspected state, 1408-step Release candidate is *unpromoted*; `champion = null`. Three heldout candidate placements [8,8,8], baseline [6,8,8], no demonstrated gain.

**Confirmed narrow behavioral failure:** saved PPO repeatedly chooses other actions when buying is legal. **Unproven mechanism:** why its logits prefer Refresh/Freeze or hero-power/cancel (observation scaling, reward, mask/action alignment, training data, or value estimation). Repeated legal-buy states are correlated, not independent opportunities, and a legal buy is not automatically the best action.

**Next causal experiment:** compare identical heldout seeds and rotating controlled seats, log public gold, legal mask and policy action probabilities; correct only one supported failure mode; separate untouched raw PPO from intervention/guarded outcomes. Do **not** expand PPO steps or promote Champion on these observations alone.

## Actual training/model outcomes of this session

- PPO gradient updates: **0**.
- New or promoted weights: **none**.
- Independently downloaded and byte-verified Release assets in this session: **none**.
- New model-controlled or paired ranking claims: **none**.
- Separate baseline canary: pending independent run and receipt; do not claim completion until Actions proves it.
- New durable model Release: **none**; prior real Releases exist but cannot be substituted for this session's own verified training.

## Release and training backlog

The repository Releases endpoint reported multiple model/model-metadata pairs including `v2-learning-41413557445` and `v5-s-20261102-68099929-1408-41428692617`. API-provided SHA256 is only the *published metadata claim* until the bytes are downloaded and rehashed. The main registry indexes a latest candidate, not a validated Champion.

Prioritize merging compatible Release download/restore into the shared training workflow after tests and exact-head CI, then enforce common heldout seeds/seat rotations, raw-vs-guarded metrics, and fully verified candidate promotion. Artifact expiration must not reset progress.

## P6 handoff / merge prerequisites

This branch is intentionally Draft until real branch-run receipt, full GitHub PR CI on final head, review of the shared training-workflow change, and concurrent-main comparison all pass. Do not merge based only on an older successful run or docs. This PR fixes one train-lineage safety bug, not PPO rank by itself.
