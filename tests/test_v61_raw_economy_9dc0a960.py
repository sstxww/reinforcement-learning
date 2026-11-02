"""Synthetic, engine-independent regressions for raw-economy evidence."""
import pytest

from tavern_ai.v61_raw_economy_9dc0a960 import ACTIONS, RawActions


def mask(*allowed):
    m = [False] * ACTIONS
    for i in allowed:
        m[i] = True
    return m


def test_zero_buy_when_buy_legal_is_measured_not_relabelled():
    s = RawActions()
    h = "a" * 64
    s.observe(turn=4, mask=mask(0, 8, 9), action=0, state_sha256=h)
    s.observe(turn=4, mask=mask(0, 8, 9), action=0, state_sha256=h)
    r = s.as_dict()
    assert r["counts"]["buy_legal_decision_exposures"] == 2
    assert r["counts"]["end_turn_with_buy_legal"] == 2
    assert r["counts"]["buy_actions"] == 0
    assert r["counts"]["unchanged_public_obs_between_decisions"] == 1
    assert r["buy_given_legal_exposure"] == 0.0


def test_count_only_actual_raw_buy_and_no_leak_across_turns():
    s = RawActions()
    m = mask(0, 8, 15, 46)
    s.observe(turn=2, mask=m, action=15, state_sha256="1" * 64)
    s.observe(turn=3, mask=m, action=46, state_sha256="1" * 64)
    r = s.as_dict()
    assert r["counts"]["buy_actions"] == 1
    assert r["counts"]["play_band"] == 1
    assert r["counts"]["unchanged_public_obs_between_decisions"] == 0
    assert r["raw_action_histogram"] == {"15": 1, "46": 1}
    assert r["buy_given_legal_exposure"] == 0.5


@pytest.mark.parametrize("action,legal", [(8, (0,)), (-1, (0,)), (245, (0,))])
def test_illegal_raw_proposal_is_rejected(action, legal):
    s = RawActions()
    with pytest.raises(ValueError, match="Illegal raw model action"):
        s.observe(turn=1, mask=mask(*legal), action=action, state_sha256="a" * 64)


def test_malformed_masks_and_digests_fail_closed():
    s = RawActions()
    with pytest.raises(ValueError, match="Invalid or empty action mask"):
        s.observe(turn=1, mask=[False] * ACTIONS, action=0, state_sha256="a" * 64)
    with pytest.raises(ValueError, match="Invalid or empty action mask"):
        s.observe(turn=1, mask=[True], action=0, state_sha256="a" * 64)
    with pytest.raises(ValueError, match="Invalid public state digest"):
        s.observe(turn=1, mask=mask(0), action=0, state_sha256="bogus")


def test_no_buy_opportunity_denominator_is_null():
    s = RawActions()
    s.observe(turn=3, mask=mask(0), action=0, state_sha256="c" * 64)
    assert s.as_dict()["buy_given_legal_exposure"] is None
