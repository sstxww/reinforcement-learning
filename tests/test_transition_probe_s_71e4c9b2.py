"""Offline pinned action-family and public-transition regression checks."""
import pytest
from tavern_ai.transition_probe_s_71e4c9b2 import action_family, public_change

@pytest.mark.parametrize("raw,family", [
    (0, "end"), (1, "refresh"), (2, "freeze"), (3, "upgrade"),
    (4, "hero_power"), (5, "hero_power"), (7, "cancel"),
    (8, "buy"), (15, "buy"), (16, "sell"), (22, "sell"),
    (30, "choose"), (45, "choose"), (46, "play"), (125, "play"),
    (126, "magnetize"), (195, "magnetize"), (196, "move"), (244, "move"),
])
def test_pinned_action_family(raw, family):
    assert action_family(raw) == family

@pytest.mark.parametrize("raw", [-1, 245, 1000, 2.0, True])
def test_reject_bad_action(raw):
    with pytest.raises(ValueError):
        action_family(raw)

def test_exact_public_bytes_detect_only_real_changes():
    state = (b"feature", b"cards", b"mask")
    same = public_change(state, state)
    assert same["unchanged_public_observation"]
    assert not any(same[k] for k in ("features_changed", "cards_changed", "mask_changed"))
    changed = public_change(state, (b"feature", b"CARD!", b"mask"))
    assert not changed["unchanged_public_observation"]
    assert not changed["features_changed"]
    assert changed["cards_changed"]
    assert not changed["mask_changed"]

def test_public_change_is_not_an_action_progress_claim():
    a = (b"f", b"c", b"m")
    assert public_change(a, (b"f", b"c", b"M"))["mask_changed"]
    with pytest.raises(TypeError):
        public_change(a, (b"f", "not-bytes", b"m"))
