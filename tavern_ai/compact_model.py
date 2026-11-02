"""Compact, independently tested TavernGym feature extractor (architecture ablation)."""
from __future__ import annotations

import torch as th
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class CompactTavernExtractor(BaseFeaturesExtractor):
    """Preserves exactly the existing Dict observation and 245-action policy API."""

    def __init__(self, observation_space, features_dim: int = 192):
        super().__init__(observation_space, features_dim=features_dim)
        n_numbers = int(observation_space["features"].shape[0])
        n_slots = int(observation_space["cards"].shape[0])
        n_card_ids = int(observation_space["cards"].high.max()) + 1
        self.embedding = nn.Embedding(n_card_ids, 4, padding_idx=0)
        self.numeric = nn.Sequential(
            nn.Linear(n_numbers, 128), nn.LayerNorm(128), nn.Tanh(),
            nn.Linear(128, 96), nn.Tanh(),
        )
        self.card_net = nn.Sequential(
            nn.Linear(n_slots * 4, 96), nn.LayerNorm(96), nn.Tanh(),
        )
        self.output = nn.Sequential(nn.Linear(192, features_dim), nn.Tanh())

    def forward(self, obs):
        numbers = obs["features"].float().clamp(-500.0, 500.0)
        cards = obs["cards"].long()
        card_embeddings = self.embedding(cards).flatten(start_dim=1)
        return self.output(th.cat(
            [self.numeric(numbers), self.card_net(card_embeddings)], dim=1
        ))
