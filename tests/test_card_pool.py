import numpy as np
import pytest

th = pytest.importorskip("torch")
pytest.importorskip("stable_baselines3")
from gymnasium import spaces
from tavern_ai.card_pool import SlotPooledExtractor

def test_forward_shape_gradient_and_empty_slots():
    space = spaces.Dict({
        "features": spaces.Box(-np.inf, np.inf, shape=(4017,), dtype=np.float32),
        "cards": spaces.Box(0, 511, shape=(447,), dtype=np.int32)})
    model = SlotPooledExtractor(space)
    cards = th.zeros((2, 447), dtype=th.int32)
    cards[0, :3] = th.tensor([4, 9, 5])
    y = model({"features": th.zeros((2, 4017)), "cards": cards})
    assert y.shape == (2, 256)
    assert th.isfinite(y).all()
    y.sum().backward()
    assert th.isfinite(model.embedding.weight.grad).all()

def test_mean_ignores_padding_and_card_order():
    cards = th.tensor([[4, 0, 9, 0], [0, 9, 4, 0], [0, 0, 0, 0]])
    table = th.arange(20, dtype=th.float32).reshape(10, 2)
    means = SlotPooledExtractor.masked_mean(cards, table[cards])
    th.testing.assert_close(means[0], means[1])
    th.testing.assert_close(means[2], th.zeros(2))
