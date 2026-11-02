"""Shape, masking and gradient tests for the isolated card bottleneck."""
import torch
from gymnasium import spaces
from tavern_ai.model import TavernExtractor


def _space():
    return spaces.Dict({
        "features": spaces.Box(-float("inf"), float("inf"), shape=(4017,)),
        "cards": spaces.Box(0, 999, shape=(447,), dtype=int),
    })


def test_forward_all_padding_is_finite_and_batched():
    module = TavernExtractor(_space())
    for batch in (1, 4):
        x = {
            "features": torch.randn(batch, 4017),
            "cards": torch.zeros(batch, 447, dtype=torch.long),
        }
        y = module(x)
        assert y.shape == (batch, 256)
        assert torch.isfinite(y).all()


def test_non_padding_card_gradients_flow_and_padding_is_fixed():
    module = TavernExtractor(_space())
    x = {
        "features": torch.randn(2, 4017),
        "cards": torch.zeros(2, 447, dtype=torch.long),
    }
    x["cards"][0, 2] = 12
    x["cards"][1, 32] = 15
    module(x).sum().backward()
    grad = module.embedding.weight.grad
    assert grad is not None
    assert torch.count_nonzero(grad[12]).item() > 0
    assert torch.count_nonzero(grad[15]).item() > 0
    assert torch.count_nonzero(grad[0]).item() == 0


def test_card_projection_has_strictly_fewer_parameters_than_v1():
    module = TavernExtractor(_space())
    new_count = sum(p.numel() for p in module.card_net.parameters())
    legacy_count = (447 * 8 + 1) * 128 + 2 * 128
    assert new_count <= 0.60 * legacy_count
