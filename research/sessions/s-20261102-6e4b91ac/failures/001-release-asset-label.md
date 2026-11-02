# V5 R001 — original GitHub Release asset label/name mismatch (resolved)

## Precise failure signature
- Original [Actions 41449706506](https://github.com/sstxww/reinforcement-learning/actions/runs/41449706506) second job `bounded-release-resume` returned **failure**, but only on the last **Publish unpromoted durable checkpoint** step.
- Earlier same-job SHA256 preflight loaded the legitimate 1408-step model, real PPO trained **+128 steps** to total **1536**, and independently checked `checkpoint_sha256=3e576d92459186a91a52940a59be0c782e8afa95fdd3323de015ab708c21db7a`.
- Exact candidate itself completed genuine pinned full eight-seat TavernGym seed **86403** (15 turns, 122 decisions, controlled placement **8**, zero truncated combats, no fallback).
- The prior shell command `gh release create ... checkpoints/resumed.zip#model.zip checkpoints/resumed.metadata.json#model.metadata.json` **did create** the versioned prerelease, but `#model.zip` only changed the displayed **label**; the asset's stored name remained `resumed.zip`. The subsequent `gh release download --pattern 'model.*'` matched nothing and failed. Original job status must remain **failed**, not misrepresented as fully successful.

## Root cause and minimal repair
- No PPO retraining, no model mutation, no overwriting another Release, and no Champion promotion.
- New isolated [Actions 41450741948](https://github.com/sstxww/reinforcement-learning/actions/runs/41450741948) **SUCCESS**: fetched original genuine `resumed.zip` and `resumed.metadata.json` from the same immutable candidate release, verified expected SHA and 1536 steps, copied same bytes to real filenames `model.zip`, `model.metadata.json`, uploaded **to the existing tag**, independently re-downloaded both assets and verified exact matching SHA256.
- Confirmed release: [v5-s-20261102-6e4b91ac-resume128](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-6e4b91ac-resume128). Verified canonical `model.zip` SHA256 `3e576d92459186a91a52940a59be0c782e8afa95fdd3323de015ab708c21db7a`; `model.metadata.json` SHA256 `76ab43f0a50682dcdb6a76117d6342336d8a8ff6956490cb4b650faee448f64e`.
- Follow-up source fix: original branch workflow changed to **manual-only** (prevents repeat push loop), unique per-run tags, copies physical files to `publish/model.zip` and `publish/model.metadata.json` before `gh release create`. This updated workflow definition still needs normal PR review/CI; the actual repair workflow already proved the core correction in Actions.

## Evidence scope
- Original training itself completed, candidate game completed (rank eight), original final asset-lookup failed, rescue job succeeded. Historic GitHub Release retains redundant original `resumed.*` assets alongside correct canonical names; this is benign, and deleting any one-of-a-kind model files was deliberately avoided.
- Champion remains null, the main scheduled `train.yml` still restores from expiring Artifacts, and a genuine n>=4 heldout paired evaluation is separate. No policy strength gain claimed.
