"""Adapter for the official TavernArena connection client; no remote execution."""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
from .contract import FEATURES,CARDS,ACTIONS
_MODEL=None

def _get_model():
    global _MODEL
    if _MODEL is None:
        file=Path(os.environ.get("TAVERN_AI_MODEL","checkpoints/model.zip"))
        if not file.is_file():raise FileNotFoundError(file)
        from sb3_contrib import MaskablePPO
        _MODEL=MaskablePPO.load(str(file),device="cpu")
    return _MODEL

def act(observation:dict,context:dict)->int:
    f=np.asarray(observation["features"],dtype=np.float32)
    c=np.asarray(observation["cards"],dtype=np.int32)
    mask=np.asarray(observation["action_mask"],dtype=bool)
    if f.shape!=(FEATURES,) or c.shape!=(CARDS,) or mask.shape!=(ACTIONS,):
        raise ValueError("Incompatible TavernArena observation; verify manifest")
    if not mask.any():raise ValueError("No legal actions")
    action,_=_get_model().predict({"features":f,"cards":c},action_masks=mask,deterministic=True)
    chosen=int(action)
    if not mask[chosen]:raise ValueError("Illegal model action")
    return chosen
