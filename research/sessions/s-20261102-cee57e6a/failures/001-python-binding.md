# Incident 001 — Python game binding mismatch (first isolated run)

- Session: s-20261102-cee57e6a, run: https://github.com/sstxww/reinforcement-learning/actions/runs/41422165613
- Failing SHA: b11d09d831be64d8f1dd7031fbad02aaf52cdbfd
- Verified Python unit tests: 16 passed.
- Verified pinned TavernGym installation: v1.1.0; engine source hash 6d8712c93022ba11; 4017 float /447 card /245 action observations.
- Failure: in the real-game entry point, AttributeError: 'builtins.Game' object has no attribute 'players'. This occurred in check_public_layout() before a candidate match could be completed.
- Root cause: confusion between the Rust Game.players internal field and its PyO3 Game interface. The documented binding exposes Game.view(seat) but not players. Baseline canary uses neither.
- Corrective action 1: validate own board/hand and minion stats against JSON-parsed game.view(0)["me"] only; do not read opponent boards or hidden state and do not pass the view into policy.act(). Also fix strict threshold equality and golden-slot regression test.
- Evidence verdict: initial run FAILED; do not claim its intermediate receipts as candidate games or promote a policy. Re-run on new commit, then update this document with re-test evidence.
