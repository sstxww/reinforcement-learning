# s-20261102-902968f5: V5 P0/P1 integration

Status: `pending_actions_verification`. Source branch based on `main@42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`.
Scope: independent Release SHA256/compatibility preflight, optimizer-resume audit and one model-controlled complete-game gate; no shared train.yml or main writes. This is not a Champion promotion.

Source candidate: versioned [V2 1,280-step experimental Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v2-learning-41413557445). Model SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`; metadata SHA256 `6f0b433191a8242dcedc627f6be49d1551a82788ce7bfd8e60416ede8146acc0` (GitHub Release API digests, not independently downloaded by this session as of initial commit).

Verified prior history: Release exists with five assets; historical V2 model-controlled match rank 8 and four heldout ranks [8,8,8,8] are documented in PR #15, which depends on #9. Current main-only train.yml restores temporary Actions artifacts, not a lasting Release. Infrastructure PR #8 has proposed registry/storage changes but is conflicted; neither #8 nor #9 is merged at initial audit.

Latest branch workflow must actually download, check SHA256, load, sample a legal action, resume 128 PPO steps, and attempt a genuine eight-player model-controlled match. Do not count claimed success before the workflow completes. Candidate after 128 steps is diagnostic-only and not durable; never overwrite existing Release/Champion. If failure occurs, save evidence, diagnose and stop instead of silently starting from scratch.

Race note: PR #25 was merged by another integrator while this session reviewed it, so this session did not merge or modify that PR. Main also integrated #26, #47, #43, #37. Avoid touching others' branches or shared train.yml. Formal integration PR pending verification.
