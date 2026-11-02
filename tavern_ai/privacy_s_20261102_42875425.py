"""Engine-backed privacy metamorphic probes for pinned TavernGym observe2.

Research-only: debug/state_json construct test fixtures. These objects are NEVER
fed to a deployable policy. The evaluated input is exactly observe2 + legal_mask.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from .contract import ACTIONS, CARDS, FEATURES, ENGINE_HASH, PATCH_SHA256, UPSTREAM_COMMIT, verify_engine

SESSION_ID = "s-20261102-42875425"
PROBE_CARD = "BG28_300"  # Verified in pinned upstream tests/test_debug.py


def model_input(game) -> tuple[bytes, bytes, bytes]:
    floats, cards = game.observe2(0)
    mask = game.legal_mask(0)
    floats, cards, mask = bytes(floats), bytes(cards), bytes(mask)
    if (len(floats), len(cards), len(mask)) != (4 * FEATURES, 4 * CARDS, ACTIONS):
        raise AssertionError("Unexpected observe2 or action-mask dimensions")
    return floats, cards, mask


def first_choice(mask: bytes) -> int:
    options = np.flatnonzero(np.frombuffer(mask, dtype=np.uint8)[30:46])
    if len(options) == 0:
        raise AssertionError("Expected a mandatory hero choice from real game state")
    return 30 + int(options[0])


def initial_recruit_state(seed: int):
    import taverngym

    game = taverngym.Game(seed=seed)
    # Game starts with independent, compulsory hero choices. Resolve these
    # through legal actions rather than editing a simulated game phase.
    for seat in range(game.num_players):
        if not game.needs_action(seat):
            raise AssertionError(f"Seat {seat} has no hero choice")
        game.step(seat, first_choice(bytes(game.legal_mask(seat))))
    if not game.needs_action(0):
        raise AssertionError("Controlled seat is not awaiting an action")
    return game


def debug(game, **command):
    game.debug(json.dumps(command, sort_keys=True))


def _hand_or_board_fixture(seed: int, zone: str, seat: int):
    import taverngym

    game = initial_recruit_state(seed)
    debug(game, cmd="add_minion", p=seat, zone=zone, card=PROBE_CARD)
    source = game.state_json()
    a = taverngym.Game.from_json(source)
    b = taverngym.Game.from_json(source)
    before = json.loads(source)["players"][seat][zone][-1]
    idx = len(json.loads(source)["players"][seat][zone]) - 1
    debug(b, cmd="edit_minion", p=seat, zone=zone, index=idx, atk=88, hp=91)
    after = json.loads(b.state_json())["players"][seat][zone][-1]
    if before == after:
        raise AssertionError(f"Failed to modify seat {seat} hidden fixture")
    if (len(json.loads(a.state_json())["players"][seat][zone])
            != len(json.loads(b.state_json())["players"][seat][zone])):
        raise AssertionError("Fixture changed a publicly observable zone count")
    return a, b


def compare(a, b, *, seed: int, zone: str, seat: int, expect_equal: bool) -> dict:
    left, right = model_input(a), model_input(b)
    equals = [x == y for x, y in zip(left, right)]
    # No internal hidden fields, RNG state or full state_json enter the model input.
    expected = all(equals) if expect_equal else not all(equals[:2])
    return {
        "seed": seed,
        "zone": zone,
        "mutated_seat": seat,
        "observer_seat": 0,
        "expected_invariant": expect_equal,
        "features_equal": equals[0],
        "cards_equal": equals[1],
        "legal_mask_equal": equals[2],
        "passed": expected,
        "baseline_input_sha256": hashlib.sha256(b"".join(left)).hexdigest(),
    }


def run_probe(seeds: tuple[int, ...] = (83011, 83012)) -> dict:
    import taverngym

    engine = verify_engine()
    tests = []
    for seed in seeds:
        # Negative controls: change only one opponent hidden instance's stats.
        # Both branches have the SAME card ID and SAME zone count.
        for zone in ("hand", "board"):
            a, b = _hand_or_board_fixture(seed, zone, seat=1)
            tests.append(compare(a, b, seed=seed, zone=zone, seat=1, expect_equal=True))
        # Positive control: same hidden-state edit performed on our OWN card
        # must be visible to our policy's observation. Prevent vacuous equality.
        a, b = _hand_or_board_fixture(seed, "hand", seat=0)
        tests.append(compare(a, b, seed=seed, zone="hand", seat=0, expect_equal=False))
    return {
        "schema": 1,
        "session_id": SESSION_ID,
        "engine_version": engine["version"],
        "engine_source_hash": ENGINE_HASH,
        "upstream_commit": UPSTREAM_COMMIT,
        "patch_sha256": PATCH_SHA256,
        "input": {"features": FEATURES, "cards": CARDS, "action_mask": ACTIONS},
        "method": "Twin Game.from_json states; modify one existing minion's attack/health using real engine debug; no rollouts or RNG inspection",
        "cases": tests,
        "passed": all(t["passed"] for t in tests),
        "interpretation": "Only same-state hidden-stat noninterference, not complete proof against all information leaks or strategy quality.",
        "model_training_steps": 0,
        "ppo_training_steps": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[83011, 83012])
    args = parser.parse_args()
    report = run_probe(tuple(args.seeds))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "cases": report["cases"]}, ensure_ascii=False))
    if not report["passed"]:
        raise SystemExit("Privacy metamorphic probe failed; do not trust model inputs")


if __name__ == "__main__":
    main()
