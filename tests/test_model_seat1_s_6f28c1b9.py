"""Synthetic tests for raw seat 1; never represent these as real game receipts."""
import numpy as np
import pytest
from tavern_ai.contract import ACTIONS, CARDS, FEATURES, ENGINE_HASH
from tavern_ai import model_seat1_s_6f28c1b9 as subject

class FakeGame:
    num_players = 8
    turn = 4
    truncated_combats = 0
    turn_limit_end = False

    def __init__(self, never_finish=False):
        self.over = False
        self.never_finish = never_finish
        self.stepped = []

    def is_over(self):
        return self.over

    def needs_action(self, seat):
        return seat == 1 and not self.over

    def bot_play(self, seat):
        raise AssertionError("opponent was not scheduled")

    def observe2(self, seat):
        assert seat == 1
        return np.zeros(FEATURES, "<f4").tobytes(), np.zeros(CARDS, "<i4").tobytes()

    def legal_mask(self, seat):
        return bytes([1] + [0] * (ACTIONS - 1))

    def step(self, seat, action):
        self.stepped.append((seat, action))
        if not self.never_finish:
            self.over = True

    def placements(self):
        return [8, 6, 3, 4, 1, 2, 5, 7]

class FakeModel:
    def __init__(self, action):
        self.action = action
        self.calls = 0

    def predict(self, obs, action_masks, deterministic):
        self.calls += 1
        assert obs["features"].shape == (FEATURES,)
        assert obs["cards"].shape == (CARDS,)
        assert action_masks.shape == (ACTIONS,)
        assert deterministic is True
        return self.action, None

def run(tmp_path, monkeypatch, game, model, **kwargs):
    monkeypatch.setattr(subject, "verify_engine", lambda: {
        "version": "1.1.0", "source_hash": ENGINE_HASH})
    checkpoint = tmp_path / "fake-not-release.zip"
    checkpoint.write_bytes(b"unit-test-only")
    return subject.play(992310, 1, "s-20261103-6f28c1b9", checkpoint,
                        model_loader=lambda path, device: model,
                        game_factory=lambda seed: game, **kwargs)

def test_seat_one_raw_action_and_placement(tmp_path, monkeypatch):
    game = FakeGame()
    model = FakeModel(0)
    rec = run(tmp_path, monkeypatch, game, model)
    assert game.stepped == [(1, 0)] and model.calls == 1
    assert rec["placements"] == [8, 6, 3, 4, 1, 2, 5, 7]
    assert rec["agent_placement"] == 6 and rec["seat"] == 1
    assert rec["policy"] == "model" and rec["fallback_actions"] == 0
    assert rec["raw_action_histogram"] == {"0": 1}

def test_illegal_action_rejected_without_fallback(tmp_path, monkeypatch):
    game = FakeGame()
    with pytest.raises(RuntimeError, match="illegal raw action"):
        run(tmp_path, monkeypatch, game, FakeModel(3))
    assert game.stepped == []

def test_incomplete_game_never_gets_rank(tmp_path, monkeypatch):
    with pytest.raises(RuntimeError, match="no placement"):
        run(tmp_path, monkeypatch, FakeGame(never_finish=True),
            FakeModel(0), max_decisions=2)

def test_invalid_seat_rejected_before_loading(tmp_path):
    with pytest.raises(ValueError, match="seat"):
        subject.play(1, 8, "s-1", tmp_path / "no.zip")

def test_wrong_production_checkpoint_hash_fails_closed(tmp_path):
    checkpoint = tmp_path / "wrong.zip"
    checkpoint.write_bytes(b"not-real-weights")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        subject.play(1, 1, "s-1", checkpoint)
