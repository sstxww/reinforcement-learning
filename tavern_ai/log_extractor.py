"""Opt-in signed-log numeric encoder. Mainline TavernExtractor remains unchanged."""
from __future__ import annotations

import torch as th
from .model import TavernExtractor


def signed_log1p(x: th.Tensor) -> th.Tensor:
    """Monotonic, odd compression preserving zero and numeric feature signs."""
    return th.sign(x) * th.log1p(x.abs())


class LogTavernExtractor(TavernExtractor):
    """Same trainable architecture as V1, differing only in numeric preprocessing."""

    def forward(self, obs):
        f = signed_log1p(obs["features"].float().clamp(-500.0, 500.0))
        c = obs["cards"].long()
        emb = self.embedding(c).flatten(start_dim=1)
        return self.output(th.cat([self.numeric(f), self.card_net(emb)], dim=1))
