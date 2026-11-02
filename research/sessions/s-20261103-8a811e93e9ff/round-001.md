# R001 — Expose CI step-label trust bypass without touching another Agent

Hypothesis: a reviewer-only gate that trusts the labels of five green GitHub Actions steps can be self-certified by a PR that rewrites its own CI job. The existing #185 gate (under independent PR review) uses the `tests-and-full-match` job with step names as proof; it does not itself fetch/validate the job's receipt or bind CI source code to trusted main. This is a **code-path vulnerability**, not evidence that any existing author exploited it.

Implemented a standalone **read-only** conservative PR changed-files preflight. It binds `main` and the PR HEAD to full immutable SHAs, paginates up to 3,000 changed files with fail-closed count checks, and refuses modifications/renames of exact trusted CI, engine, canary, receipt-validation and dependency files. Synthetic tests cover a successfully named but fake canary, incomplete pages, renamed validators, malformed paths and stale SHAs. It never merges, changes refs, or downloads/publishes models.

Limitations / nonclaims: protected path list is defense in depth; other imported Python can still affect behavior. The ultimate integration solution MUST execute a verifier from trusted main and validate a real original eight-seat run artifact, not infer authenticity from step-name success. The fix is intentionally isolated and does **not** modify #185's branch or its integration script.

Observed initial main SHA: `c1b828734527bae6141805581693d890cc3bff94`; main CI #41512315964 initially in progress. Parent registered unpromoted model 1408-step SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. This session generated **0** new PPO steps, 0 raw PPO games, 0 Release, 0 Champion promotions. Dedicated real TavernGym baseline seed 99679 must be checked before claiming completion; synthetic tests aren't games.

No main integration lock held. After own smoke/CI and true receipt, submit patch PR and precisely hand off source-trust gate usage to the #185 integrator.
