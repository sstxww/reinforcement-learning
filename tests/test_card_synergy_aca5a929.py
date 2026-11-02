"""Contract checks for card-aware ranking. Full mechanics validation occurs on engine in CI."""
import numpy as np
import pytest
from tavern_ai.card_synergy_aca5a929 import Weights, best_buy, card_offsets


DIMS = {"N_POWERS":2,"N_QUESTS":3,"N_SECRETS":5,"N_BOARD":7,
        "N_HAND":10,"N_SHOP":8,"OBS_CARDS":447,"N_ACTIONS":245}


def sample():
    cards=np.zeros(447,dtype=np.int32)
    mask=np.zeros(245,dtype=bool)
    mask[8]=True
    mask[9]=True
    catalog=np.zeros((8,70),dtype=np.float32)
    catalog[1,0]=catalog[3,0]=catalog[4,0]=1  # minion kind
    catalog[1,15]=catalog[3,15]=1            # matching race
    catalog[4,16]=1                           # different race
    catalog[3,11]=catalog[3,12]=3
    catalog[4,11]=catalog[4,12]=8
    board,hand,shop=card_offsets(DIMS)
    cards[board]=1
    cards[shop]=3
    cards[shop+1]=4
    return {"cards":cards,"action_mask":mask},catalog


def test_card_stream_offsets_match_upstream_observe2():
    assert card_offsets(DIMS)==(19,26,36)


def test_public_tribe_overlap_changes_purchase_target():
    o,s=sample()
    assert best_buy(o,Weights(stat=1,tier=0,race=0),s,DIMS)==9
    assert best_buy(o,Weights(stat=1,tier=0,race=2,pair=0),s,DIMS)==8


def test_pair_reward_uses_visible_hand_and_board_only():
    o,s=sample()
    board,hand,shop=card_offsets(DIMS)
    o["cards"][board]=3
    o["cards"][hand]=3
    assert best_buy(o,Weights(stat=1,tier=0,race=0,pair=3.5),s,DIMS)==8


def test_mask_is_respected_and_no_legal_minion_returns_none():
    o,s=sample()
    o["action_mask"][8]=False
    assert best_buy(o,Weights(race=100),s,DIMS)==9
    o["action_mask"][9]=False
    assert best_buy(o,Weights(),s,DIMS) is None


def test_non_minion_shop_spell_ignored():
    o,s=sample()
    _,_,shop=card_offsets(DIMS)
    o["cards"][shop]=2  # kind flags all zero: not a minion
    assert best_buy(o,Weights(),s,DIMS)==9


def test_incompatible_observation_rejected():
    o,s=sample()
    o["cards"]=o["cards"][:100]
    with pytest.raises(ValueError,match="shape"):
        best_buy(o,Weights(),s,DIMS)
