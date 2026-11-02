# s-20261102-ba09e2d4 — Round 001 executed status

- Initial main: `f29a0a6e99161aca4163e51427f6bfabbe02f76f`. Other independent sessions merged PRs during audit.
- Initial GitHub audit: 68 open PRs, six Releases, current CI success. Relevant #9 Draft dependency, #15 depends on #9; #25 strict receipt validation Draft; #43 subsequently merged elsewhere.
- Implemented and pushed opt-in SHA256/metadata/optimizer checkpoint structure gate, tests, unpromoted model registry, documentation and finite Actions workflow.
- Actual own baseline full eight-seat TavernGym game: [Actions 41427340311](https://github.com/sstxww/reinforcement-learning/actions/runs/41427340311) completed SUCCESS, seed 87101, rank 7, 47 decisions, 15 turns, zero truncations and zero turn-limit guard. True receipt in `experiments/s-20261102-ba09e2d4/001-87101.json`.
- First-run model training: 0 steps. No new weights/checkpoint. No Champion.
- PR #60 provides reason to test legal BUY opportunities in model-controlled runs, not enough to conclude low learning rate is causal.
- Follow-up implementation: isolated real-model action-opportunity probe, release hash verification, paired same-seed baseline in a separate finite branch-only workflow. Outcome pending, not represented as verified yet.
- Full PR #80 stays Draft until independent latest-head PR CI and compatibility review. 

## Real R001 failure-loop correction
- Job [41427938674](https://github.com/sstxww/reinforcement-learning/actions/runs/41427938674) failed after successful real V2 Release download, before model load, because the initial inspector rejected actual metadata `schema: 2`. It is a schema compatibility error, not proof of checkpoint corruption.
- Original learning PR #9 source code explicitly writes schema-2 `checkpoint_sha256` and `compatibility`; code has now been adjusted to validate both. Synthetic regression tests cover positive schema 2 and negative wrong hash/compatibility. This is repair attempt 1 of at most 2; awaiting real rerun.
- Independent PR CI run [41427946441](https://github.com/sstxww/reinforcement-learning/actions/runs/41427946441) succeeded on previous source head. Post-repair latest-head CI must be confirmed separately.
- Main has now integrated #87 independent registry, so this PR's duplicate registry must be reconciled instead of merging two canonical sources.
