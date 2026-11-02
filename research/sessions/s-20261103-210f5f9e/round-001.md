# R001 — prove unprotected main cannot have assumed exclusive integration
Session: s-20261103-210f5f9e; task integrate/main-protection-preflight; base main c1b828734527bae6141805581693d890cc3bff94.

## Inherited GitHub evidence
- V7 full 32,014-byte email attachment read.
- Issue #182 https://github.com/sstxww/reinforcement-learning/issues/182 documents actual concurrent #164 merge while a CAS coordination-ref lease was held. The ref CAS worked but nonparticipant merger bypassed it.
- GET branch main: protected=false, protection.enabled=false, no enforced required status checks. GET rulesets returned [] at check time. These findings are snapshots, not a promise about future settings.
- Main #165 merged with current exact SHA as above; postmerge run 41512315964 was in progress at the first inspection.
- PR #175 current full-game CI success is NOT merge permission: two independent reviews found samefile→unlink rollback TOCTOU that can delete another writer's replacement.

## Change and falsifiable hypothesis
A preflight that only checks a coordination ref produces a false positive. Add a deliberately fail-closed read-only merge audit that parses live branch protection and active main-scoped Merge Queue facts, always prevents global-exclusivity claims from those facts alone, and describes blockers. Add synthetic negative tests for unprotected main, stale SHA, no queue, irrelevant queue, and queue that still lacks all-writer routing proof.
This is an engineering negative gate, not an enforced serialized merge queue.

## Bounded real test plan
Own workflow: read-only GH token; 45-minute timeout; unique concurrency; unit regressions, live branch settings, pinned TavernGym contract, and one genuine eight-seat baseline seed 99817. The baseline result is infrastructure evidence, not PPO model evidence. Only commit original completed game receipt after reading actual Actions artifact and logs. If a job fails, preserve first error and rerun only after a material fix.

## Model and execution limits
No new PPO steps, no trained checkpoint, no new Release, no registry modification, no model strength gain, no formal TavernArena.
Registered latest still 1408-step V5 unpromoted model, hash a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632. Historical paired heldout 1408 model ranks [8,8,8], baseline [6,8,8], n=3.

## Next owner
Verify unique real workflow receipt and own PR latest HEAD CI, then use a truly enforced GitHub Merge Queue or a user-designated single integrator. Do not merge via our diagnostic, which cannot grant exclusion.
