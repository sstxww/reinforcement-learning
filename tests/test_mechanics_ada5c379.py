"""Offline ABI regression tests; no engine installation or match state needed."""
import numpy as np
import pytest

from tavern_ai.mechanics_ada5c379 import (
    WIDTH, extract, make_summary, verify_known_cases,
)


class FakeCardEngine:
    N_CARDS = 3

    def __init__(self):
        self.values = np.zeros((3, WIDTH), dtype="<f4")
        self.values[1, 0] = 1  # minion
        self.values[1, 10:15] = (2, 3, 4, 3, 0)
        self.values[1, 15] = 1  # BEAST
        self.values[1, 37 + 1] = 1  # DIVINE_SHIELD
        self.values[1, 49 + 1] = 1  # DEATHRATTLE
        self.values[1, 61] = 1  # in minion pool
        self.values[2, 2] = 1  # regular spell
        self.values[2, 10] = 3
        self.values[2, 13] = 1
        self.ids = ["", "SAMPLE_MINION", "SAMPLE_SPELL"]

    def card_static(self):
        return WIDTH, self.values.tobytes()

    def card_info(self, idx):
        return self.ids[idx], "Sample", "例", int(self.values[idx, 10])


def test_static_mapping_without_hidden_game_state():
    result = extract(FakeCardEngine())
    assert result["provenance"]["model_card_indices"] == 3
    assert len(result["provenance"]["runtime_card_table_sha256"]) == 64
    a, b = result["cards"]
    assert a["index"] == 1 and a["id"] == "SAMPLE_MINION"
    assert a["races"] == ["BEAST"]
    assert a["keywords"] == ["DIVINE_SHIELD"]
    assert a["mechanics"] == ["DEATHRATTLE"]
    assert a["pools"] == ["minion"]
    assert a["attack"] == 3 and a["health"] == 4
    assert b["kind"] == "spell" and b["index"] == 2
    assert "rng" not in a and "opponent_hand" not in a
    assert result["provenance"]["static_feature_width"] == 66


def test_schema_mismatch_fails_closed():
    f = FakeCardEngine()
    f.card_static = lambda: (65, f.values.tobytes())
    with pytest.raises(ValueError, match="schema drift"):
        extract(f)


def test_bad_row_count_fails_closed():
    f = FakeCardEngine()
    f.card_static = lambda: (WIDTH, f.values[:2].tobytes())
    with pytest.raises(ValueError, match="size drift"):
        extract(f)


def test_nonbinary_keywords_fails_closed():
    f = FakeCardEngine()
    f.values[1, 38] = 0.5
    with pytest.raises(ValueError, match="nonbinary"):
        extract(f)


def test_padding_and_tier_mismatch_fails_closed():
    f = FakeCardEngine()
    f.values[0, 1] = 1
    with pytest.raises(ValueError, match="padding"):
        extract(f)
    f.values[0, 1] = 0
    f.card_info = lambda idx: (f.ids[idx], "Sample", "例", 9)
    with pytest.raises(ValueError, match="tier mismatch"):
        extract(f)


def test_duplicate_ids_rejected():
    f = FakeCardEngine()
    f.ids[2] = f.ids[1]
    with pytest.raises(ValueError, match="duplicate"):
        extract(f)


def test_claims_do_not_confuse_schema_with_executable_mechanics():
    result = extract(FakeCardEngine())
    with pytest.raises(ValueError, match="missing upstream"):
        verify_known_cases(result)
    # No assertion of win-rate or training steps is emitted without a real engine.
    assert result["provenance"]["warning"].startswith("Metadata flags")
