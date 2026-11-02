"""Bounded post-purchase board-space policy, TavernGym 1.1.0.

Public action indices: buy 8..15; sell 16..22; play 46..125;
magnetize 126..195. Not a neural model or trained PPO.
"""
from dataclasses import dataclass, field
import numpy as np
from .baseline import BaselinePolicy

@dataclass
class SellCyclePolicy:
    budget: int = 1
    baseline: BaselinePolicy = field(default_factory=BaselinePolicy)
    turn_seen: int = -1
    pending_buy: bool = False
    sells_this_turn: int = 0
    total_sells: int = 0
    forced_ends: int = 0

    def __post_init__(self):
        if not isinstance(self.budget, int) or not 0 <= self.budget <= 2:
            raise ValueError("budget must be 0..2")

    def act(self, observation: dict, context: dict | None = None) -> int:
        context = context or {}
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (245,) or not mask.any():
            raise ValueError("Expected nonempty TavernGym 245-action mask")
        turn = int(context.get("turn", 0))
        used = int(context.get("actions_used", 0))
        if turn != self.turn_seen:
            self.turn_seen = turn
            self.pending_buy = False
            self.sells_this_turn = 0
        if used >= 85 and mask[0]:
            self.forced_ends += 1
            self.pending_buy = False
            return 0
        if (self.pending_buy and self.sells_this_turn < self.budget
                and not mask[30:46].any()
                and not (mask[46:126].any() or mask[126:196].any())):
            sells = np.flatnonzero(mask[16:23])
            if len(sells):
                action = int(16 + sells[0])
                self.sells_this_turn += 1
                self.total_sells += 1
                self.pending_buy = False
                return action
        action = self.baseline.act(observation, context)
        if not mask[action]:
            raise ValueError("Illegal baseline action")
        if 8 <= action <= 15:
            self.pending_buy = True
        elif action == 0 or 46 <= action <= 195:
            self.pending_buy = False
        return action
