"""Isolated card-embedding optional-width smoke tests (skip without train extras)."""
import pytest

th = pytest.importorskip("torch")
pytest.importorskip("stable_baselines3")
from gymnasium import spaces
from tavern_ai.model import TavernExtractor

def test_card_embedding_widths_preserve_shape():
    obs_space = spaces.Dict({
        "features": spaces.Box(-1e6, 1e6, shape=(4017,), dtype=float),
        "cards": spaces.Box(0, 449, shape=(447,), dtype=int)
    })
    obs = {"features": th.zeros((2, 4017), dtype=th.float32),
           "cards": th.zeros((2, 447), dtype=th.int64)}
    for dim in (8, 16):
        extractor = TavernExtractor(obs_space, features_dim=256, card_embedding_dim=dim)
        assert extractor.embedding.embedding_dim == dim
        assert extractor(obs).shape == (2, 256)

def test_invalid_width_is_rejected():
    obs_space = spaces.Dict({
        "features": spaces.Box(-1e6, 1e6, shape=(4017,), dtype=float),
        "cards": spaces.Box(0, 449, shape=(447,), dtype=int)
    })
    with pytest.raises(ValueError):
        TavernExtractor(obs_space, card_embedding_dim=0)
