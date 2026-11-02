"""Experimental, non-padding card-set pooling alongside positional card slots."""
from __future__ import annotations
import torch as th
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class SlotPooledExtractor(BaseFeaturesExtractor):
    """Ablation only: the original TavernExtractor is unchanged."""
    def __init__(self, observation_space, features_dim: int = 256):
        super().__init__(observation_space, features_dim=features_dim)
        vocab = int(observation_space["cards"].high.max()) + 1
        slots = int(observation_space["cards"].shape[0])
        numbers = int(observation_space["features"].shape[0])
        self.embedding = nn.Embedding(vocab, 8, padding_idx=0)
        self.numeric = nn.Sequential(nn.Linear(numbers, 192), nn.LayerNorm(192),
                                     nn.Tanh(), nn.Linear(192, 128), nn.Tanh())
        self.positional = nn.Sequential(nn.Linear(slots * 8, 96), nn.LayerNorm(96), nn.Tanh())
        self.pooled = nn.Sequential(nn.Linear(8, 32), nn.LayerNorm(32), nn.Tanh())
        self.output = nn.Sequential(nn.Linear(256, features_dim), nn.Tanh())

    @staticmethod
    def masked_mean(cards: th.Tensor, embeddings: th.Tensor) -> th.Tensor:
        valid = (cards != 0).unsqueeze(-1)
        return (embeddings * valid).sum(dim=1) / valid.sum(dim=1).clamp_min(1)

    def forward(self, obs):
        features = obs["features"].float().clamp(-500.0, 500.0)
        cards = obs["cards"].long()
        embeds = self.embedding(cards)
        pooled = self.masked_mean(cards, embeds)
        joined = th.cat([self.numeric(features),
                         self.positional(embeds.flatten(start_dim=1)),
                         self.pooled(pooled)], dim=1)
        return self.output(joined)
