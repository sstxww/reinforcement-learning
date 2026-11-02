"""Regression: TavernGym legacy observation card count != patched observe2 count.

With the engine installed, this verifies the *actual* public board/hand/shop
card prefix, rather than accepting a synthetic 447-slot layout as proof.
"""
import numpy as np
import pytest

from tavern_ai.card_synergy_aca5a929 import card_offsets
from tavern_ai.contract import CARDS, FEATURES


def test_legacy_offsets_and_arena_dimensions_are_different_contracts():
    layout={"N_POWERS":2,"N_QUESTS":3,"N_SECRETS":5,
            "N_BOARD":7,"N_HAND":10,"N_SHOP":8,"OBS_CARDS":124}
    assert card_offsets(layout)==(19,26,36)
    assert (CARDS,FEATURES)==(447,4017)
    assert layout["OBS_CARDS"] != CARDS


def test_real_engine_observe2_keeps_own_public_card_prefix():
    taverngym=pytest.importorskip("taverngym",reason="requires pinned patched Rust engine")
    from tavern_ai.contract import verify_engine
    verify_engine()
    g=taverngym.Game(seed=79110)
    before=np.frombuffer(g.observe(0)[1],dtype="<i4")
    after=np.frombuffer(g.observe2(0)[1],dtype="<i4")
    layout=dict(taverngym.layout())
    assert before.shape == (layout["OBS_CARDS"],)
    assert after.shape == (CARDS,)
    assert np.array_equal(before,after[:len(before)])
