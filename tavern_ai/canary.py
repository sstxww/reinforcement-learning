"""Real complete eight-seat TavernGym simulation, with signed-off JSON receipt."""
from __future__ import annotations
import argparse,hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from .baseline import BaselinePolicy
from .contract import FEATURES,CARDS,ACTIONS,verify_engine
from .validate_receipt import validate

def run(seed:int,agent_id:str,policy:str="baseline",model_path:str|None=None)->dict:
    import taverngym
    if not agent_id or "/" in agent_id or "\\" in agent_id:raise ValueError("Invalid agent id")
    engine=verify_engine()
    game=taverngym.Game(seed=seed)
    baseline=BaselinePolicy()
    model=None
    if policy=="model":
        if not model_path or not Path(model_path).is_file():raise FileNotFoundError(model_path)
        from sb3_contrib import MaskablePPO
        model=MaskablePPO.load(model_path,device="cpu")
    elif policy!="baseline":raise ValueError("Policy must be baseline or model")
    decisions=0
    actions_this_turn=0
    last_turn=-1
    for _ in range(30000):
        if game.is_over():break
        turn=int(game.turn)
        if turn!=last_turn:last_turn,actions_this_turn=turn,0
        progress=False
        for seat in range(game.num_players):
            if not game.needs_action(seat):continue
            progress=True
            if seat!=0:
                game.bot_play(seat)
                continue
            fbytes,cbytes=game.observe2(0)
            f=np.frombuffer(fbytes,dtype="<f4").copy()
            c=np.frombuffer(cbytes,dtype="<i4").copy()
            mask=np.frombuffer(game.legal_mask(0),dtype=np.uint8).astype(bool)
            if f.shape!=(FEATURES,) or c.shape!=(CARDS,) or mask.shape!=(ACTIONS,):
                raise ValueError("Unexpected observe2 contract")
            if model is None:
                action=baseline.act({"features":f,"cards":c,"action_mask":mask},
                                    {"turn":turn,"actions_used":actions_this_turn})
            else:
                action,_=model.predict({"features":f,"cards":c},action_masks=mask,deterministic=True)
                action=int(action)
            if not mask[int(action)]:raise ValueError("Illegal policy action")
            game.step(0,int(action))
            actions_this_turn+=1
            decisions+=1
        if not progress and not game.is_over():raise RuntimeError("Game stalled")
    if not game.is_over():raise RuntimeError("Full-game safety limit exceeded")
    result={
        "schema":1,"timestamp":datetime.now(timezone.utc).isoformat(),
        "environment":"TavernGym","engine_source_hash":engine["source_hash"],
        "engine_version":engine["version"],"agent_id":agent_id,"policy":policy,
        "seed":seed,"completed":True,"turns":int(game.turn),
        "decisions":decisions,"placements":[int(x) for x in game.placements()],
        "truncated_combats":int(game.truncated_combats),
        "turn_limit_end":bool(game.turn_limit_end),
        "git_sha":os.getenv("GITHUB_SHA",""),
        "model_sha256":hashlib.sha256(Path(model_path).read_bytes()).hexdigest() if model_path else None,
    }
    validate(result)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--seed",type=int,default=1001)
    parser.add_argument("--agent-id",required=True)
    parser.add_argument("--policy",choices=["baseline","model"],default="baseline")
    parser.add_argument("--model")
    parser.add_argument("--receipt",type=Path,required=True)
    a=parser.parse_args()
    result=run(a.seed,a.agent_id,a.policy,a.model)
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    a.receipt.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
