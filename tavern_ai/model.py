"""PPO feature extractor with float and card-embedding branches.

The card path uses a position-preserving low-rank bottleneck. Compared with
the V1 447*8 -> 128 dense projection, a 64-wide intermediate representation
reduces trainable weights while retaining distinct coefficients for each slot.
"""
from __future__ import annotations

import torch as th
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class TavernExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim: int = 256):
        super().__init__(observation_space, features_dim=features_dim)
        card_count = int(observation_space["cards"].high.max()) + 1
        n_slots = int(observation_space["cards"].shape[0])
        n_numbers = int(observation_space["features"].shape[0])
        self.embedding = nn.Embedding(card_count, 8, padding_idx=0)
        self.numeric = nn.Sequential(
            nn.Linear(n_numbers, 192), nn.LayerNorm(192), nn.Tanh(),
            nn.Linear(192, 128), nn.Tanh(),
        )
        # A low-rank factorization of the position-aware card projection.
        # Unlike mean pooling it preserves board/shop/hand slot identity.
        self.card_net = nn.Sequential(
            nn.Linear(n_slots * 8, 64), nn.LayerNorm(64), nn.Tanh(),
            nn.Linear(64, 128), nn.Tanh(),
        )
        self.output = nn.Sequential(nn.Linear(256, features_dim), nn.Tanh())

    def forward(self, obs):
        f = obs["features"].float().clamp(-500.0, 500.0)
        c = obs["cards"].long()
        emb = self.embedding(c).flatten(start_dim=1)
        return self.output(th.cat([self.numeric(f), self.card_net(emb)], dim=1))
