"""Reproducible microbenchmark comparing V1 and low-rank card extractors.

This is an inference throughput/parameter comparison, NOT game-performance
evidence. Run on CPU with single-thread PyTorch to limit scheduling noise.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import numpy as np
import torch
from gymnasium import spaces
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from tavern_ai.model import TavernExtractor


class V1TavernExtractor(BaseFeaturesExtractor):
    """Verbatim architectural reference from main commit 6ac59235."""
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
        self.card_net = nn.Sequential(
            nn.Linear(n_slots * 8, 128), nn.LayerNorm(128), nn.Tanh(),
        )
        self.output = nn.Sequential(nn.Linear(256, features_dim), nn.Tanh())

    def forward(self, obs):
        f = obs["features"].float().clamp(-500.0, 500.0)
        c = obs["cards"].long()
        emb = self.embedding(c).flatten(start_dim=1)
        return self.output(torch.cat([self.numeric(f), self.card_net(emb)], dim=1))


def benchmark(cls, space, obs):
    torch.manual_seed(22020)
    net = cls(space).eval()
    with torch.no_grad():
        for _ in range(8):
            net(obs)
        durations = []
        for _ in range(40):
            start = time.perf_counter()
            out = net(obs)
            durations.append(1000 * (time.perf_counter() - start))
    assert torch.isfinite(out).all()
    return {
        "parameters_total": sum(p.numel() for p in net.parameters()),
        "parameters_card_net": sum(p.numel() for p in net.card_net.parameters()),
        "ms_per_batch_median": statistics.median(durations),
        "ms_per_batch_p90": sorted(durations)[35],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(1)
    torch.manual_seed(22020)
    space = spaces.Dict({
        "features": spaces.Box(-np.inf, np.inf, shape=(4017,), dtype=np.float32),
        "cards": spaces.Box(0, 999, shape=(447,), dtype=np.int32),
    })
    obs = {
        "features": torch.randn(16, 4017),
        "cards": torch.randint(0, 999, (16, 447)),
    }
    old = benchmark(V1TavernExtractor, space, obs)
    new = benchmark(TavernExtractor, space, obs)
    result = {
        "schema": 1, "base_commit": "6ac59235b8238196a0e6462de77b72413c829372",
        "seed": 22020, "batch_size": 16, "warmups": 8, "timed_batches": 40,
        "torch_threads": 1, "old": old, "candidate": new,
        "total_parameter_reduction_fraction":
            1 - new["parameters_total"] / old["parameters_total"],
        "card_parameter_reduction_fraction":
            1 - new["parameters_card_net"] / old["parameters_card_net"],
        "note": "CPU microbenchmark; not a measure of relative playing strength",
    }
    assert result["card_parameter_reduction_fraction"] >= 0.4
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
