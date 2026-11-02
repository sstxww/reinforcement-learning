# Failure 001 — preserve the existing Seat/rank error-message contract

- **Session / task:** `s-20261103-f6994f077b`, `v7/seat-attestation-integrity`, round 001.
- **Initial PR head:** `42d3ae70f1eff75c7429ee651ab522206a5374a7`.
- **Original failing PR CI:** [run #41513738257](https://github.com/sstxww/reinforcement-learning/actions/runs/41513738257), job `125511837696`, **failure**.
- **Precise signature:** `tests/test_paired_receipt_gate_v5_15ac04d0.py::test_seat_mismatch_rejected` expected `pytest.raises(ValueError, match="Seat/rank")`; actual thrown `ValueError("Agent placement does not match controlled seat")`. Result: **404 passed, 1 skipped, 1 failed**.
- **Established root cause:** The strict upstream `receipt_integrity.validate_integrity()` now rejects the invalid controlled seat/claimed placement earlier than the pre-existing downstream paired-gate check. This changes the exception string without changing the intended rejection. The existing test's error-matching contract was not preserved.
- **Not a simulator/model failure:** The separately executed real eight-seat original baseline game already completed in [run #41512909874](https://github.com/sstxww/reinforcement-learning/actions/runs/41512909874); it was not part of this failed unit step. No PPO/training/model performance inferred.
- **Minimal correction (first substantive fix):** Keep the stricter rejection, but use the message `Seat/rank mismatch: Agent placement does not match controlled seat` so the existing and new test expectations agree without editing tests or other workers' modules.
- **Retest gate:** Require fresh full PR CI, with unit suite, independent eight-seat CI game and receipt gate, on the commit containing the fix. Do **not** claim green until that run truly succeeds.
- **Retries:** first failure; one substantive fix planned. No blind retry of unchanged SHA, no model weights or checkpoint altered.
- **Integration policy:** No unique integrator lock, no main merge. Keep PR #213 reviewable but blocked from merge until latest-head CI success and exclusive integrator acceptance.
