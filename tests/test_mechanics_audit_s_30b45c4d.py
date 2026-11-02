import json

import pytest

from tavern_ai.mechanics_audit_s_30b45c4d import (
    ACTION_FAMILIES, action_family, build_catalog, decode_action,
)


def test_exact_pinned_action_partition():
    indices = [i for _, lo, hi in ACTION_FAMILIES for i in range(lo, hi)]
    assert len(indices) == 245
    assert sorted(indices) == list(range(245))
    assert [action_family(i) for i in indices][:8] == [
        "end_turn", "refresh", "freeze", "upgrade", "hero_power",
        "hero_power", "dark_gift", "cancel",
    ]
    with pytest.raises(ValueError):
        action_family(245)
    with pytest.raises(ValueError):
        action_family(-1)


@pytest.mark.parametrize("action,expected", [
    (8, {"family": "buy", "slot": 0}),
    (15, {"family": "buy", "slot": 7}),
    (16, {"family": "sell", "slot": 0}),
    (22, {"family": "sell", "slot": 6}),
    (30, {"family": "choose", "slot": 0}),
    (45, {"family": "choose", "slot": 15}),
    (46, {"family": "play", "hand": 0, "position": 0}),
    (53, {"family": "play", "hand": 0, "position": 7}),
    (125, {"family": "play", "hand": 9, "position": 7}),
    (126, {"family": "magnetize", "hand": 0, "board": 0}),
    (195, {"family": "magnetize", "hand": 9, "board": 6}),
    (196, {"family": "move", "from": 0, "to": 0}),
    (244, {"family": "move", "from": 6, "to": 6}),
])
def test_actions_decode_from_upstream(action, expected):
    assert decode_action(action) == expected


def _write_catalog(path, cards, patch="36.6.3"):
    path.write_text(json.dumps({
        "meta": {"server_patch": patch, "client_version": "test"},
        "cards": cards,
    }), encoding="utf-8")


def _card(cid, pool):
    return {
        "id": cid, "kind": "minion", "name": cid, "name_zh": "",
        "tier": 2, "atk": 3, "hp": 4, "races": ["BEAST"],
        "keywords": ["DEATHRATTLE"], "pools": pool,
        "text": "Some text (not verified implementation)",
    }


def test_catalog_keeps_out_of_pool_and_zero_padding(tmp_path):
    source = tmp_path / "cards.json"
    _write_catalog(source, [_card("A", ["minion"]), _card("B", [])])
    records, summary = build_catalog(source)
    assert [c["observation_card_index"] for c in records] == [1, 2]
    assert summary["card_count"] == 2
    assert summary["pool_counts"] == {"minion": 1}
    assert summary["cards_without_pools"] == 1
    assert records[1]["pools"] == []
    assert records[0]["effect_verification"] == "NOT_VERIFIED_BY_TEXT"
    assert len(summary["source_file_sha256"]) == 64


def test_catalog_rejects_duplicates_and_wrong_patch(tmp_path):
    source = tmp_path / "cards.json"
    _write_catalog(source, [_card("A", []), _card("A", [])])
    with pytest.raises(ValueError, match="Duplicate"):
        build_catalog(source)
    _write_catalog(source, [_card("A", [])], patch="36.6.4")
    with pytest.raises(ValueError, match="ruleset"):
        build_catalog(source)
