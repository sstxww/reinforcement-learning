"""Targeted numerical preprocessing tests; no simulator needed."""
from __future__ import annotations
import pytest

th = pytest.importorskip("torch")
pytest.importorskip("stable_baselines3")
gym = pytest.importorskip("gymnasium")

from tavern_ai.log_extractor import LogTavernExtractor, signed_log1p
from tavern_ai.model import TavernExtractor


def test_signed_log_zero_sign_and_bounded_dynamic_range():
    inp = th.tensor([-500.0, -4.0, -1.0, 0.0, 1.0, 4.0, 500.0])
    out = signed_log1p(inp)
    assert th.isfinite(out).all()
    assert th.equal(out, -out.flip(0))
    assert float(out[3]) == 0.0
    assert bool(th.all(out[1:] >= out[:-1]))
    assert float(out.max()) < 7.0


def test_both_extractors_same_shapes_and_finite_outputs():
    spaces = gym.spaces.Dict({
        "features": gym.spaces.Box(-float("inf"), float("inf"), (4017,), dtype="float32"),
        "cards": gym.spaces.Box(0, 999, (447,), dtype="int32"),
    })
    obs = {"features": th.randn(2, 4017) * 100,
           "cards": th.randint(0, 1000, (2, 447))}
    for cls in (TavernExtractor, LogTavernExtractor):
        th.manual_seed(77)
        extractor = cls(spaces, features_dim=256)
        with th.no_grad():
            result = extractor(obs)
        assert result.shape == (2, 256)
        assert bool(th.isfinite(result).all())
