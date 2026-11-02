"""Deterministic legal-action V0 baseline. Not a competitive game strategy."""
from __future__ import annotations
import numpy as np

# Prevent pathological action loops from monopolizing the shop phase.
# Mandatory hero/discover choices still take precedence over this budget.
MAX_ACTIONS_PER_TURN = 48

class BaselinePolicy:
    def act(self, observation: dict, context: dict | None = None) -> int:
        context = context or {}
        mask = np.asarray(observation["action_mask"],dtype=bool)
        if mask.shape != (245,) or not mask.any():
            raise ValueError("Expected 245-action nonempty mask")
        turn = int(context.get("turn",0))
        used = int(context.get("actions_used",0))
        if used < 0:
            raise ValueError("Negative action count")
        def first(lo,hi):
            xs=np.flatnonzero(mask[lo:hi])
            return int(xs[0]+lo) if len(xs) else None
        # Never skip forced draft/discover decisions.
        choice=first(30,46)
        if choice is not None:return choice
        if used >= MAX_ACTIONS_PER_TURN and mask[0]:return 0
        # Resolve playable hand cards and available targeted actions first.
        for lo,hi in ((46,126),(126,196)):
            a=first(lo,hi)
            if a is not None:return a
        if turn in {2,5,7,9,11} and mask[3]:return 3
        buy=first(8,16)
        if buy is not None:return buy
        if mask[3]:return 3
        if mask[0]:return 0
        return int(np.flatnonzero(mask)[0])
