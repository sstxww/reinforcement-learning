"""Explicit and optional, mask-legal loop guard; not original PPO behavior."""
from __future__ import annotations
from collections import deque
import numpy as np
from .contract import ACTIONS

class HeroCancelGuard:
    def __init__(self):
        self._turn = None
        self._actions = deque(maxlen=4)
        self.interventions = 0

    def select(self, turn: int, proposed: int, action_mask) -> int:
        mask = np.asarray(action_mask, dtype=bool)
        if mask.shape != (ACTIONS,) or not mask.any():
            raise ValueError("Expected nonempty 245-action mask")
        if not isinstance(proposed, int) or not 0 <= proposed < ACTIONS or not mask[proposed]:
            raise ValueError("Model proposed illegal action")
        if type(turn) is not int or turn < 0:
            raise ValueError("Invalid game turn")
        if turn != self._turn:
            self._turn = turn
            self._actions.clear()
        h = list(self._actions)
        oscillates = (len(h) == 4 and h[0] in (4, 5) and h[1] == 7 and
                      h[2] in (4, 5) and h[3] == 7)
        override = proposed in (4, 5) and oscillates and bool(mask[0])
        chosen = 0 if override else proposed
        if override:
            self.interventions += 1
        if not mask[chosen]:
            raise ValueError("Guard may not select an illegal action")
        self._actions.append(chosen)
        return chosen
