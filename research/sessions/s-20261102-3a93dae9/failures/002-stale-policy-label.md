# Failure 002 — Incorrect historical policy descriptor in second batch

failure_signature: receipt policy metadata stale after modifying rule
run: https://github.com/sstxww/reinforcement-learning/actions/runs/41416155846
source_SHA: 82b71762edc35c23b63b0d93c50e9336a37ff5d1
affected_seeds: 18101–18106
actual_issue: the six receipts label policy free_hero_power_once_per_turn although the versioned source code already implements <=3 gold, >=3 reserve and turn>=3. Actual source code SHA256 edce76c81671d5b51cea3c012f3b0595bf95194afa8ea838b2e1510ff6807c2e. Game and other fields are real.
root_cause: rule changed but string literal did not.
repair: explicit POLICY_NAME constant used in receipt; add unit regression for exact label and reserve threshold. Preserve original six receipts as raw historical evidence; DO NOT silently edit completed-game provenance.
verified_in: https://github.com/sstxww/reinforcement-learning/actions/runs/41416624735 (SUCCESS, 25 tests passed, 6 complete independent candidate games with policy affordable_hero_power_gold_reserve_v2; record SHA256 a6aba2d5f349911dfebf568c2fdbae305bf4c1adb07ee23eaef339c80bd72e0a).
status: fixed in new run; earlier original metadata remains explicitly annotated in round report.
