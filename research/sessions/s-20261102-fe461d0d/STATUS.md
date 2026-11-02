# s-20261102-fe461d0d STATUS — completed R001 smoke, no strength gain

- Session: `s-20261102-fe461d0d`; Draft integration PR [#117](https://github.com/sstxww/reinforcement-learning/pull/117).
- Main starting SHA: `db5e23ae8c218808821327d806b05d2604cfadfb`; branch base: `1afd8297e3c661bee3117ac5301b1ca08d64869b`.
- P0 PR #93 integration blocker: comment `6577783113` on its outdated four-candidate tests.
- P1 full genuine GitHub Actions run [#41450034817](https://github.com/sstxww/reinforcement-learning/actions/runs/41450034817): **success**, pinned TavernGym 1.1.0 `6d8712c93022ba11`, all validate/test/restore/train/game/release steps succeeded.
- Existing canonical **source** Release: `v5-s-20261102-68099929-1408-41428692617` (SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`), two asset digests checked and actual CPU model loaded.
- **Real PPO continuation**: +128 steps, 1408 → **1536 cumulative**; this session's genuine updated candidate saved in a separate file.
- Candidate model SHA256: `c2c456e72164e0819b9793955c10832234f43dfc7bd1da76187e6b912f2c89c2`.
- **Durable, unpromoted** prerelease: [v5-s-20261102-fe461d0d-smoke-41450034817-1](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-fe461d0d-smoke-41450034817-1). Published model.zip + model.metadata.json + game and paired receipts; both critical assets were re-downloaded and byte compared. This candidate is **not** registered as latest or Champion.
- Authentic own baseline full game seed `52611`: seat0 rank **8**, 14 turns, 36 decisions, `completed=true`; `experiments/s-20261102-fe461d0d/001-52611.json`.
- Authentic own **model-only**, no baseline substitution, seed `52612`: seat0 rank **8**, 15 turns, 111 decisions, `completed=true`, 0 truncated combats and no turn-limit ending; `experiments/s-20261102-fe461d0d/002-52612.json`. Exact receipt bytes SHA256 `0194506f33185d86ff34852c981d5f26d288d42a9dfb982c23ebd3afa8fece4f` match published Release.
- Exploratory one-seed independent paired evaluation seed `52614`: candidate rank **8**, baseline rank **8**, delta 0; `reports/s-20261102-fe461d0d/001-paired.json`, exact published SHA256 `10a82980ab31805ef5b4c40cb70b85ec3751d357a14e6d3e1fcb5d13c7bcadcc`. **n=1 is not enough to claim competitive strength.**
- All own PPO training: **128 actual steps**, 1 baseline full game + 1 candidate full game + 2 paired full games = **4 genuine completed eight-seat TavernGym games**. No official Arena.
- PR CI initially: `240 passed, 1 skipped` but failed missing own receipt before workflow committed it, run [#41450089924](https://github.com/sstxww/reinforcement-learning/actions/runs/41450089924). Bot receipt commit spawned `action_required` run #41450575800; latest-head CI must be rerun on user-authored commit.
- **NO model improvement, no Champion/Best promotion, no main merge claimed.** Main `train.yml` remains unchanged until PR #117 passes final review and is merged.
- P2 follow-up: use latest true opportunity and Play↔Cancel traces; analyze missing board growth and no-progress actions before further expansion.
