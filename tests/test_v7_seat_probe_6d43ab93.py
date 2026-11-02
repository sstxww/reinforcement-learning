"""Offline contract regression for the isolated nonzero-seat V7 probe.

Synthetic game objects are TEST FIXTURES, never actual match evidence.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location(
    "v7_seat_probe_6d43ab93",
    Path(__file__).resolve().parents[1] / "scripts" / "v7_seat_probe_6d43ab93.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class FakeFinishedGame:
    turn = 14
    truncated_combats = 0
    turn_limit_end = False

    def placements(self):
        return [3, 7, 6, 8, 1, 4, 2, 5]


ENGINE = {"version": "1.1.0", "source_hash": "6d8712c93022ba11"}
DIAGNOSTICS = {"raw_action_histogram": {"0": 4}}


@pytest.mark.parametrize("seat", [0, -1, 8, True, "1"])
def test_probe_rejects_bad_seat(seat):
    with pytest.raises(ValueError, match="non-zero"):
        probe.validate_settings(99741, seat, "baseline", 100)


@pytest.mark.parametrize("seed,budget", [(-1, 100), (99741, 0), (99741, 6001)])
def test_probe_budgets_fail_closed(seed, budget):
    with pytest.raises(ValueError):
        probe.validate_settings(seed, 1, "model", budget)


def test_baseline_controlled_seat_one_is_rank_seven_not_seat_zero():
    r = probe.complete_receipt(
        engine=ENGINE, game=FakeFinishedGame(), seed=99741, seat=1,
        policy="baseline", decisions=50, model_sha=None,
        diagnostics=DIAGNOSTICS)
    assert r["completed"] is True
    assert r["seat"] == 1
    assert r["agent_placement"] == 7
    assert r["placements"][0] == 3
    assert r["model_sha256"] is None
    assert r["fallback_actions"] == r["guard_forced_ends"] == 0


def test_model_receipt_has_own_weight_hash_and_no_fallback():
    r = probe.complete_receipt(
        engine=ENGINE, game=FakeFinishedGame(), seed=99741, seat=1,
        policy="model", decisions=100, model_sha="a" * 64,
        diagnostics=DIAGNOSTICS)
    assert r["agent_placement"] == 7
    assert r["model_sha256"] == "a" * 64
    assert r["fallback_actions"] == 0


def test_model_without_hash_fails_closed():
    with pytest.raises(ValueError, match="SHA256"):
        probe.complete_receipt(
            engine=ENGINE, game=FakeFinishedGame(), seed=99741, seat=1,
            policy="model", decisions=100, model_sha=None,
            diagnostics=DIAGNOSTICS)


def test_invalid_permutation_rejected():
    class BadGame(FakeFinishedGame):
        def placements(self):
            return [3, 7, 6, 8, 1, 4, 2, 2]
    with pytest.raises(ValueError, match="permutation"):
        probe.complete_receipt(
            engine=ENGINE, game=BadGame(), seed=99741, seat=1,
            policy="baseline", decisions=100, model_sha=None,
            diagnostics=DIAGNOSTICS)
