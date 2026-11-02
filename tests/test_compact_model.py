"""Architecture smoke tests; no TavernGym install required."""
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("stable_baselines3")
from gymnasium import spaces
import numpy as np
from tavern_ai.compact_model import CompactTavernExtractor
from tavern_ai.model import TavernExtractor


def _space():
    return spaces.Dict({
        "features": spaces.Box(-np.inf, np.inf, (4017,), np.float32),
        "cards": spaces.Box(0, 9999, (447,), np.int32),
    })


def test_compact_extractor_preserves_observations_and_has_fewer_parameters():
    space = _space()
    original = TavernExtractor(space, features_dim=256)
    compact = CompactTavernExtractor(space, features_dim=192)
    n_orig = sum(p.numel() for p in original.parameters())
    n_compact = sum(p.numel() for p in compact.parameters())
    assert n_compact < n_orig
    out = compact({
        "features": torch.randn(2, 4017),
        "cards": torch.zeros(2, 447, dtype=torch.int64),
    })
    assert out.shape == (2, 192)
    assert bool(torch.isfinite(out).all())
