"""No synthetic match receipts: small pure-math unit tests only."""
import numpy as np
import pytest
from tavern_ai.mechanics_probe_0ecd90f7 import (
    GROUPS, availability, prepare, fit_probe, sigmoid, compare
)


def test_exact_upstream_action_partitions():
    assert list(GROUPS.items()) == [
        ("refresh", (1, 2)), ("freeze", (2, 3)),
        ("upgrade", (3, 4)), ("buy", (8, 16)),
        ("sell", (16, 23)), ("choose", (30, 46)),
        ("play", (46, 126)), ("magnetize", (126, 196)),
    ]
    mask = np.zeros(245, dtype=bool)
    mask[[1, 3, 15, 22, 45, 125, 195]] = True
    assert availability(mask).tolist() == [1, 0, 1, 1, 1, 1, 1, 1]
    with pytest.raises(ValueError):
        availability(np.ones(244))


def test_feature_selection_only_uses_training_states():
    x = np.zeros((4, 10), dtype=np.float32)
    x[:, 2] = [0, 1, 2, 3]
    eval_x = np.zeros((2, 10), dtype=np.float32)
    eval_x[:, 5] = 9999
    train, heldout, cols, mu, sd = prepare(x, eval_x, width=2)
    assert cols[0] == 2
    assert 5 not in cols
    assert train.shape == (4, 2)
    assert heldout.shape == (2, 2)
    assert np.isfinite(heldout).all()


def test_gradient_steps_improve_separable_mask_family():
    x = np.array([[-2], [-1], [1], [2]] * 10, dtype=np.float32)
    y = (x > 0).astype(np.float32)
    w, b = fit_probe(x, y, iterations=240)
    z = sigmoid(x @ w + b)
    assert ((z >= .5) == (y > 0)).all()
    assert float(np.mean((z-y)**2)) < .25


def test_metrics_preserve_real_label_prevalence():
    y = np.array([[1]*8, [0]*8], dtype=np.float32)
    p = np.array([[.9]*8, [.1]*8], dtype=np.float32)
    summary = compare(y, p, np.ones(8, dtype=np.float32) * .5)
    assert summary["buy"]["tp"] == 1
    assert summary["buy"]["tn"] == 1
    assert summary["buy"]["model_brier"] < summary["buy"]["train_prior_brier"]
