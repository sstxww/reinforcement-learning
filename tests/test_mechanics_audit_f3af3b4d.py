"""Pure unit tests; separate actual-engine tests run in the isolated workflow."""
import pytest

from tavern_ai.mechanics_audit_f3af3b4d import action_family, normalize_catalog, ACTION_FAMILIES
from tavern_ai.contract import ACTIONS

def test_every_action_index_has_exactly_one_source_partition():
    assert ACTION_FAMILIES[0][0] == 0
    assert ACTION_FAMILIES[-1][1] == ACTIONS
    for a, b in zip(ACTION_FAMILIES, ACTION_FAMILIES[1:]):
        assert a[1] == b[0]
    assert len([action_family(i) for i in range(ACTIONS)]) == ACTIONS
    with pytest.raises(ValueError):
        action_family(-1)
    with pytest.raises(ValueError):
        action_family(ACTIONS)

def test_card_catalog_rejects_reordering_and_duplicates():
    def card(cid, name):
        return dict(cid=cid, id=name, name=name, name_zh=name, kind="minion",
                    tier=1, atk=1, hp=1, cost=0, races=[], implemented=True,
                    scripted=False, reachable=True, in_pool=True, golden_id=None,
                    normal_id=None, hero_power_id=None, tier7=False)
    good = [card(0, "A"), card(1, "B")]
    assert len(normalize_catalog(good)) == 2
    with pytest.raises(ValueError):
        normalize_catalog([good[1], good[0]])
    with pytest.raises(ValueError):
        normalize_catalog([good[0], card(1, "A")])
    with pytest.raises(ValueError):
        normalize_catalog([dict(cid=0, id="x")])
