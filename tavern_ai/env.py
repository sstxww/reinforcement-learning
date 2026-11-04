"""Gymnasium wrapper for patched single-seat TavernGym observe2."""
from __future__ import annotations
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from .contract import FEATURES,CARDS,ACTIONS,verify_engine
from .action_identity import require_discrete_action

class TavernEnv(gym.Env):
    metadata={"render_modes":[]}
    def __init__(self,seed:int=0,verify:bool=True):
        super().__init__()
        import taverngym
        if verify:verify_engine()
        self.game=taverngym.BattlegroundsEnv(seed=seed,observation_version=2)
        self.action_space=spaces.Discrete(ACTIONS)
        self.observation_space=spaces.Dict({
          "features":spaces.Box(low=-np.inf,high=np.inf,shape=(FEATURES,),dtype=np.float32),
          "cards":spaces.Box(low=0,high=taverngym.N_CARDS-1,shape=(CARDS,),dtype=np.int32),
        })
        self._mask=np.ones(ACTIONS,dtype=bool)
        self._seed_counter=seed
    def _map(self,obs):
        f=np.asarray(obs["features"],dtype=np.float32).copy()
        c=np.asarray(obs["cards"],dtype=np.int32).copy()
        mask=np.asarray(obs["action_mask"],dtype=bool).copy()
        if f.shape!=(FEATURES,) or c.shape!=(CARDS,) or mask.shape!=(ACTIONS,):
            raise ValueError("Observation sizes do not match pinned contract")
        if not np.isfinite(f).all():raise ValueError("Non-finite features")
        if (c<0).any() or (c>=self.observation_space["cards"].high.max()+1).any():
            raise ValueError("Out-of-range card index")
        self._mask=mask
        return {"features":f,"cards":c}
    def action_masks(self):return self._mask.copy()
    def reset(self,*,seed=None,options=None):
        super().reset(seed=seed)
        if seed is None:
            self._seed_counter+=1
            seed=self._seed_counter
        else:self._seed_counter=seed
        obs,info=self.game.reset(seed=int(seed))
        return self._map(obs),info
    def step(self,action):
        action=require_discrete_action(action)
        if action<0 or action>=ACTIONS or not self._mask[action]:
            raise ValueError(f"Illegal action: {action}")
        obs,reward,terminated,truncated,info=self.game.step(action)
        return self._map(obs),float(reward),bool(terminated),bool(truncated),info
    def close(self):self.game=None
