"""Regression checks for the session-scoped public-observation privacy probe."""
import numpy as np
import pytest

from tavern_ai.privacy_s_20261102_42875425 import first_choice, model_input, run_probe


class DummyGame:
    def __init__(self, flen=4017 * 4, clen=447 * 4, mlen=245):
        self.flen, self.clen, self.mlen = flen, clen, mlen

    def observe2(self, seat):
        assert seat == 0
        return b"\0" * self.flen, b"\0" * self.clen

    def legal_mask(self, seat):
        return b"\1" * self.mlen


def test_model_input_contract_with_stub():
    f, c, m = model_input(DummyGame())
    assert (len(f), len(c), len(m)) == (4017 * 4, 447 * 4, 245)
    for bad in (DummyGame(flen=3), DummyGame(clen=123), DummyGame(mlen=244)):
        with pytest.raises(AssertionError, match="dimensions"):
            model_input(bad)


def test_first_hero_choice_is_a_masked_option():
    mask = np.zeros(245, dtype=np.uint8)
    mask[32] = 1
    mask[35] = 1
    assert first_choice(mask.tobytes()) == 32
    with pytest.raises(AssertionError, match="mandatory hero choice"):
        first_choice(np.zeros(245, dtype=np.uint8).tobytes())


def test_engine_hidden_vs_own_state_noninterference():
    # CI's regular pytest stage occurs before installing the pinned engine;
    # dedicated experiment runs this test *after* bootstrap_engine.sh.
    pytest.importorskip("taverngym")
    r = run_probe((83010,))
    assert len(r["cases"]) == 3
    assert r["passed"], r["cases"]
    assert all(c["legal_mask_equal"] for c in r["cases"])
    assert all(c["passed"] for c in r["cases"])
